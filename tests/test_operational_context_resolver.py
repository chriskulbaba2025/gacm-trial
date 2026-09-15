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
from gacm.context import (  # noqa: E402
    ContextCandidate,
    ContextResolver,
    OperationRequirements,
    SourceProvenance,
    candidate_from_handoff,
)
from gacm.context.requirements import SUPPORTED_CONTEXT_FIELDS  # noqa: E402


def run_git(cwd, *args):
    completed = subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return completed.stdout.strip()


class ContextFixture:
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
        (self.repo / "config" / "operations.json").write_text("authoritative operations\n", encoding="utf-8")
        run_git(self.repo, "add", ".")
        run_git(self.repo, "commit", "-m", "context fixture")
        run_git(self.repo, "remote", "add", "origin", self.remote.as_uri())
        run_git(self.repo, "push", "-u", "origin", "main")
        self.sha = run_git(self.repo, "rev-parse", "HEAD")
        self.remote_identity = AuthorityResolver(
            ResolverConfig(repository_path=self.repo, intended_branch="main", authorized_head=self.sha, protected_rollback_sha=self.sha)
        ).resolve()
        self.blob_sha = run_git(self.repo, "rev-parse", f"{self.sha}:config/operations.json")

    def close(self):
        self.temp.cleanup()


class OperationalContextResolverTests(unittest.TestCase):
    def setUp(self):
        self.fixture = ContextFixture()
        self.requirements = OperationRequirements(
            operation="deploy-staging",
            required_fields=SUPPORTED_CONTEXT_FIELDS,
            expected_project="project-1",
            expected_repository=self.fixture.remote_identity.repository,
            expected_environment="staging",
        )

    def tearDown(self):
        self.fixture.close()

    def candidate(self, field, value, **overrides):
        provenance = {
            "source_kind": "GITHUB",
            "source_path": "config/operations.json",
            "source_blob_sha": self.fixture.blob_sha,
            "source_git_head": self.fixture.sha,
            "repository_id": self.fixture.remote_identity.repository,
            "project_id": "project-1",
            "environment": "staging",
            "github_proof": True,
        }
        provenance.update(overrides)
        return ContextCandidate(field, value, SourceProvenance(**provenance))

    def complete_candidates(self):
        values = {
            "project": "project-1",
            "client": "client-1",
            "repository": self.fixture.remote_identity.repository,
            "branch": "main",
            "environment": "staging",
            "cloud_account": {"provider": "aws", "account_id": "acct-1"},
            "tenant": "tenant-1",
            "region": "ca-central-1",
            "deployment_target": "staging-target",
            "service": "api",
            "database": "db-staging",
            "credential_reference": "cred/staging",
            "domain": "staging.example.invalid",
            "external_integration_identity": "integration-1",
        }
        return [self.candidate(field, value) for field, value in values.items()]

    def resolver(self, requirements=None, authority=None):
        return ContextResolver(requirements or self.requirements, authority or self.fixture.remote_identity, self.fixture.repo)

    def test_complete_unambiguous_context_is_verified(self):
        snapshot = self.resolver().resolve(self.complete_candidates())
        self.assertEqual("VERIFIED", snapshot.status)
        self.assertEqual(set(SUPPORTED_CONTEXT_FIELDS), set(snapshot.values))
        self.assertEqual(len(snapshot.sources), len(SUPPORTED_CONTEXT_FIELDS))

    def test_required_account_missing_is_blocked(self):
        candidates = [candidate for candidate in self.complete_candidates() if candidate.field != "cloud_account"]
        snapshot = self.resolver().resolve(candidates)
        self.assertEqual("BLOCKED", snapshot.status)

    def test_two_authoritative_accounts_are_ambiguous(self):
        candidates = self.complete_candidates() + [self.candidate("cloud_account", {"provider": "aws", "account_id": "acct-2"})]
        snapshot = self.resolver().resolve(candidates)
        self.assertEqual("AMBIGUOUS", snapshot.status)

    def test_graphify_candidate_without_github_proof_is_rejected(self):
        candidates = self.complete_candidates()
        candidates[0] = ContextCandidate(
            "project",
            "project-1",
            SourceProvenance("GRAPHIFY", "config/operations.json", self.fixture.blob_sha, self.fixture.sha, self.fixture.remote_identity.repository, "project-1", "staging", github_proof=False),
        )
        snapshot = self.resolver().resolve(candidates)
        self.assertEqual("BLOCKED", snapshot.status)

    def test_verified_github_backed_candidate_is_accepted(self):
        snapshot = self.resolver().resolve(self.complete_candidates())
        self.assertEqual("VERIFIED", snapshot.status)
        self.assertTrue(all(source["github_proof"] for source in snapshot.sources))

    def test_wrong_project_provenance_is_rejected(self):
        candidates = self.complete_candidates()
        candidates[0] = self.candidate("project", "other-project", project_id="other-project")
        self.assertEqual("BLOCKED", self.resolver().resolve(candidates).status)

    def test_wrong_repository_provenance_is_rejected(self):
        candidates = self.complete_candidates()
        candidates[1] = self.candidate("client", "client-1", repository_id="other/repository")
        self.assertEqual("BLOCKED", self.resolver().resolve(candidates).status)

    def test_wrong_environment_provenance_is_rejected(self):
        candidates = self.complete_candidates()
        candidates[1] = self.candidate("client", "client-1", environment="production")
        self.assertEqual("BLOCKED", self.resolver().resolve(candidates).status)

    def test_chat_memory_only_value_is_rejected(self):
        candidates = self.complete_candidates()
        candidates[1] = ContextCandidate(
            "client", "remembered-client", SourceProvenance("CHAT", "chat", self.fixture.blob_sha, self.fixture.sha, self.fixture.remote_identity.repository, "project-1", "staging", github_proof=False)
        )
        self.assertEqual("BLOCKED", self.resolver().resolve(candidates).status)

    def test_placeholder_value_is_rejected(self):
        candidates = self.complete_candidates()
        candidates[7] = self.candidate("region", "<ACCOUNT_ID>")
        self.assertEqual("BLOCKED", self.resolver().resolve(candidates).status)

    def test_verified_context_projects_into_phase_two_run_state(self):
        snapshot = self.resolver().resolve(self.complete_candidates())
        patch = snapshot.to_run_state_patch(self.fixture.sha)
        state = json.loads((ROOT / "tests" / "fixtures" / "valid_new_run.json").read_text(encoding="utf-8"))
        state.update(patch)
        schema = json.loads((ROOT / "schemas" / "gacm-run-state.schema.json").read_text(encoding="utf-8"))
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(state))
        self.assertEqual([], errors)

    def test_work_unit_snapshot_does_not_inherit_source_change(self):
        snapshot = self.resolver().resolve(self.complete_candidates())
        snapshot.assert_unchanged(self.fixture.sha, {"config/operations.json": self.fixture.blob_sha})
        with self.assertRaises(RuntimeError):
            snapshot.assert_unchanged(self.fixture.sha, {"config/operations.json": "0" * 40})
        self.assertEqual("VERIFIED", snapshot.status)

    def test_context_cannot_create_authoritative_pass(self):
        snapshot = self.resolver().resolve(self.complete_candidates())
        output = snapshot.to_dict()
        self.assertNotIn("verification", output)
        self.assertNotIn("authoritative_pass", output)
        self.assertNotEqual("PASS", output["status"])

    def test_handoff_builder_requires_github_source_proof(self):
        with self.assertRaises(ValueError):
            candidate_from_handoff("project", "project-1", {"source_path": "config/operations.json"}, "project-1", self.fixture.remote_identity.repository)


if __name__ == "__main__":
    unittest.main()
