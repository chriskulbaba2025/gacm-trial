import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gacm.authority import AuthorityResolver, ResolverConfig  # noqa: E402


def run_git(cwd, *args):
    completed = subprocess.run(
        ["git", *args], cwd=cwd, text=True, capture_output=True, check=False
    )
    if completed.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {completed.stderr}")
    return completed.stdout.strip()


class GitFixture:
    def __init__(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.remote = self.root / "remote.git"
        self.work = self.root / "work"
        run_git(self.root, "init", "--bare", str(self.remote))
        run_git(self.root, "init", "-b", "main", str(self.work))
        run_git(self.work, "config", "user.email", "gacm-test@example.invalid")
        run_git(self.work, "config", "user.name", "GACM Test")
        (self.work / "CURRENT_STATE.md").write_text("state\n", encoding="utf-8")
        (self.work / "GACM_IMPLEMENTATION_PRD_V1.0.md").write_text("prd\n", encoding="utf-8")
        (self.work / "tracked.txt").write_text("initial\n", encoding="utf-8")
        run_git(self.work, "add", ".")
        run_git(self.work, "commit", "-m", "initial authority fixture")
        run_git(self.work, "remote", "add", "origin", self.remote.as_uri())
        run_git(self.work, "push", "-u", "origin", "main")
        self.initial_sha = run_git(self.work, "rev-parse", "HEAD")

    def close(self):
        self.temp.cleanup()

    def commit_local(self, name, content):
        (self.work / name).write_text(content, encoding="utf-8")
        run_git(self.work, "add", name)
        run_git(self.work, "commit", "-m", "local change")

    def clone_and_push(self, name, content):
        clone = self.root / name
        run_git(self.root, "clone", "--branch", "main", self.remote.as_uri(), str(clone))
        run_git(clone, "config", "user.email", "gacm-test@example.invalid")
        run_git(clone, "config", "user.name", "GACM Test")
        (clone / "remote.txt").write_text(content, encoding="utf-8")
        run_git(clone, "add", "remote.txt")
        run_git(clone, "commit", "-m", "remote change")
        run_git(clone, "push", "origin", "main")

    def config(self, **overrides):
        values = {
            "repository_path": self.work,
            "intended_branch": "main",
            "authorized_head": self.initial_sha,
            "protected_rollback_sha": self.initial_sha,
        }
        values.update(overrides)
        return ResolverConfig(**values)


class GithubAuthorityResolverTests(unittest.TestCase):
    def setUp(self):
        self.fixture = GitFixture()

    def tearDown(self):
        self.fixture.close()

    def resolve(self, **overrides):
        return AuthorityResolver(self.fixture.config(**overrides)).resolve()

    def test_matching_clean_local_remote_state_is_verified(self):
        result = self.resolve()
        self.assertEqual("VERIFIED", result.status)
        self.assertEqual("MATCH", result.divergence)
        self.assertTrue(result.worktree_clean)
        self.assertEqual(self.fixture.initial_sha, result.local_head)
        self.assertEqual(self.fixture.initial_sha, result.remote_head)
        self.assertEqual([], result.blocking_reasons)

    def test_dirty_worktree_is_blocked(self):
        (self.fixture.work / "tracked.txt").write_text("dirty\n", encoding="utf-8")
        result = self.resolve()
        self.assertEqual("BLOCKED", result.status)
        self.assertIn("worktree is dirty", " ".join(result.blocking_reasons))

    def test_local_ahead_of_remote_is_blocked(self):
        self.fixture.commit_local("local.txt", "ahead\n")
        result = self.resolve()
        self.assertEqual("BLOCKED", result.status)
        self.assertEqual("AHEAD", result.divergence)

    def test_remote_ahead_of_local_is_blocked(self):
        self.fixture.clone_and_push("remote-ahead", "ahead\n")
        result = self.resolve()
        self.assertEqual("BLOCKED", result.status)
        self.assertEqual("BEHIND", result.divergence)

    def test_diverged_histories_are_blocked(self):
        self.fixture.commit_local("local.txt", "local\n")
        self.fixture.clone_and_push("remote-diverged", "remote\n")
        result = self.resolve(authorized_head=None)
        self.assertEqual("BLOCKED", result.status)
        self.assertEqual("DIVERGED", result.divergence)

    def test_missing_required_authority_file_is_blocked(self):
        (self.fixture.work / "CURRENT_STATE.md").unlink()
        result = self.resolve()
        self.assertEqual("BLOCKED", result.status)
        self.assertEqual(["CURRENT_STATE.md"], result.missing_authority_files)

    def test_wrong_branch_is_blocked(self):
        result = self.resolve(intended_branch="release", intended_ref="refs/heads/main")
        self.assertEqual("BLOCKED", result.status)
        self.assertIn("governed target branch", " ".join(result.blocking_reasons))

    def test_repository_identity_mismatch_is_blocked(self):
        result = self.resolve(expected_repository="other/project")
        self.assertEqual("BLOCKED", result.status)
        self.assertFalse(result.repository_identity_match)

    def test_unresolved_remote_ref_is_ambiguous(self):
        result = self.resolve(intended_ref="refs/heads/not-present")
        self.assertEqual("AMBIGUOUS", result.status)
        self.assertTrue(result.ambiguous_reasons)

    def test_verified_result_projects_into_phase_two_run_state(self):
        result = self.resolve()
        self.assertEqual("VERIFIED", result.status)
        patch = result.to_run_state_patch(self.fixture.config())
        state = json.loads(
            (ROOT / "tests" / "fixtures" / "valid_new_run.json").read_text(encoding="utf-8")
        )
        state.update(patch)
        schema = json.loads(
            (ROOT / "schemas" / "gacm-run-state.schema.json").read_text(encoding="utf-8")
        )
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(state))
        self.assertEqual([], errors)

    def test_cli_emits_machine_readable_result(self):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "gacm.authority",
                "--repo",
                str(self.fixture.work),
                "--branch",
                "main",
                "--authorized-head",
                self.fixture.initial_sha,
            ],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual("VERIFIED", json.loads(completed.stdout)["status"])


if __name__ == "__main__":
    unittest.main()
