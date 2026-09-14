import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gacm.authority import AuthorityResolver, ResolverConfig  # noqa: E402
from gacm.authority.resolver import ResolutionResult  # noqa: E402
from gacm.discovery import GraphifyAdapter, GraphifyConfig, handoff_candidates  # noqa: E402
from gacm.discovery.graphify_adapter import CommandResult, discovery_evidence  # noqa: E402


def run_git(cwd, *args):
    completed = subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return completed.stdout.strip()


class AuthorityFixture:
    def __init__(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.remote = root / "remote.git"
        self.repo = root / "repo"
        run_git(root, "init", "--bare", str(self.remote))
        run_git(root, "init", "-b", "main", str(self.repo))
        run_git(self.repo, "config", "user.email", "gacm-test@example.invalid")
        run_git(self.repo, "config", "user.name", "GACM Test")
        (self.repo / "CURRENT_STATE.md").write_text("state\n", encoding="utf-8")
        (self.repo / "GACM_IMPLEMENTATION_PRD_V1.0.md").write_text("prd\n", encoding="utf-8")
        (self.repo / "config").mkdir()
        (self.repo / "config" / "staging.toml").write_text("environment = 'staging'\n", encoding="utf-8")
        run_git(self.repo, "add", ".")
        run_git(self.repo, "commit", "-m", "discovery fixture")
        run_git(self.repo, "remote", "add", "origin", self.remote.as_uri())
        run_git(self.repo, "push", "-u", "origin", "main")
        self.sha = run_git(self.repo, "rev-parse", "HEAD")
        self.authority = AuthorityResolver(
            ResolverConfig(
                repository_path=self.repo,
                intended_branch="main",
                authorized_head=self.sha,
                protected_rollback_sha=self.sha,
            )
        ).resolve()

    def close(self):
        self.temp.cleanup()


class GraphifyDiscoveryAdapterTests(unittest.TestCase):
    def setUp(self):
        self.fixture = AuthorityFixture()
        self.query = "Which configuration controls staging deployment?"
        self.config = GraphifyConfig(
            command=("graphify-test",),
            repository_path=self.fixture.repo,
            query=self.query,
            repository_identity="example/gacm",
        )

    def tearDown(self):
        self.fixture.close()

    def runner(self, payload):
        def execute(command, input_text, timeout, cwd):
            return CommandResult(0, json.dumps(payload))

        return execute

    def candidate(self, source_path="config/staging.toml", query=None):
        return {
            "source_path": source_path,
            "source_type": "config",
            "relationship": "controls_environment",
            "target": "staging",
            "confidence": 0.98,
            "query": query or self.query,
            "repository": "example/gacm",
        }

    def discover(self, payload):
        return GraphifyAdapter(self.config, runner=self.runner(payload)).discover()

    def test_valid_single_discovery_candidate(self):
        result = self.discover({"candidates": [self.candidate()]})
        self.assertEqual("DISCOVERED", result.status)
        self.assertEqual("config/staging.toml", result.candidates[0].source_path)
        self.assertEqual(str(self.fixture.repo.resolve()), result.candidates[0].workspace)

    def test_multiple_candidates_are_ambiguous(self):
        result = self.discover({"candidates": [self.candidate(), self.candidate("config/other.toml")]})
        self.assertEqual("AMBIGUOUS", result.status)

    def test_no_result_is_no_match(self):
        result = self.discover({"candidates": []})
        self.assertEqual("NO_MATCH", result.status)

    def test_graphify_unavailable_is_error(self):
        def unavailable(command, input_text, timeout, cwd):
            raise FileNotFoundError("graphify")

        result = GraphifyAdapter(self.config, runner=unavailable).discover()
        self.assertEqual("ERROR", result.status)

    def test_malformed_graphify_output_is_error(self):
        result = GraphifyAdapter(
            self.config,
            runner=lambda command, input_text, timeout, cwd: CommandResult(0, "not-json"),
        ).discover()
        self.assertEqual("ERROR", result.status)

    def test_candidate_without_provenance_is_rejected(self):
        candidate = self.candidate()
        del candidate["source_path"]
        result = self.discover({"candidates": [candidate]})
        self.assertEqual("ERROR", result.status)
        self.assertIn("provenance", result.error)

    def test_candidate_source_missing_from_verified_git_state_is_rejected(self):
        result = self.discover({"candidates": [self.candidate("config/missing.toml")]})
        handoff = handoff_candidates(result, self.fixture.authority, self.fixture.repo)
        self.assertEqual("REJECTED", handoff.status)
        self.assertTrue(handoff.rejection_reasons)

    def test_candidate_source_present_in_verified_git_state_is_accepted_for_handoff(self):
        result = self.discover({"candidates": [self.candidate()]})
        handoff = handoff_candidates(result, self.fixture.authority, self.fixture.repo)
        self.assertEqual("ACCEPTED_FOR_AUTHORITY_RESOLUTION", handoff.status)
        self.assertEqual(self.fixture.sha, handoff.candidates[0]["source_git_head"])
        self.assertNotEqual("VERIFIED", handoff.status)

    def test_graphify_result_cannot_create_authoritative_pass(self):
        result = self.discover({"candidates": [self.candidate()]})
        self.assertNotEqual("VERIFIED", result.status)
        self.assertNotIn("authoritative", result.to_dict())
        evidence = discovery_evidence(result, "graph-evidence-1", "2026-09-14T16:00:00Z")
        self.assertNotEqual("PASS", evidence.get("status"))

    def test_graphify_result_cannot_override_github_authority(self):
        result = self.discover({"candidates": [self.candidate()]})
        blocked_authority = ResolutionResult(status="BLOCKED", local_head=self.fixture.sha)
        handoff = handoff_candidates(result, blocked_authority, self.fixture.repo)
        self.assertEqual("REJECTED", handoff.status)

    def test_discovery_evidence_records_in_phase_two_state_without_authority(self):
        result = self.discover({"candidates": [self.candidate()]})
        evidence = discovery_evidence(result, "graph-evidence-2", "2026-09-14T16:00:00Z")
        state = json.loads((ROOT / "tests" / "fixtures" / "valid_new_run.json").read_text(encoding="utf-8"))
        state.setdefault("evidence", []).append(evidence)
        state["work_units"][0]["input_evidence"].append(evidence["evidence_id"])
        schema = json.loads((ROOT / "schemas" / "gacm-run-state.schema.json").read_text(encoding="utf-8"))
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(state))
        self.assertEqual([], errors)
        self.assertEqual("RESOLVED", state["operational_context"]["resolution_status"])
        self.assertNotIn("authoritative_pass", result.to_dict())


if __name__ == "__main__":
    unittest.main()
