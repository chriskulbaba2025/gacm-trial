import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gacm.verification import GitDiffEvidenceReader, IndependentVerificationEngine, VerificationInput  # noqa: E402


START = "a" * 40
END = "b" * 40


def base_input(**overrides):
    contract = {
        "run_id": "run-verify",
        "work_unit_id": "unit-verify",
        "authorized_start_sha": START,
        "repository_id": "repo-gacm",
        "branch": "main",
        "worktree": "C:/work/gacm",
        "context_snapshot_id": "ctx-1",
        "context_snapshot_revision": "1",
        "selected_model": "gpt-5.6-luna",
        "qualification_identity": "qual-luna-1",
        "routing_decision_id": "route-1",
    }
    receipt = {
        "run_id": "run-verify",
        "work_unit_id": "unit-verify",
        "execution_id": "exec-1",
        "starting_sha": START,
        "ending_sha": END,
        "model_used": "gpt-5.6-luna",
        "qualification_identity": "qual-luna-1",
        "files_changed": ["src/local.py"],
        "execution_status": "COMPLETED",
        "authoritative_pass": False,
    }
    values = {
        "run_state": {"run_id": "run-verify"},
        "work_unit_contract": contract,
        "execution_receipt": receipt,
        "starting_repository": {"sha": START, "repository_id": "repo-gacm", "branch": "main", "worktree": "C:/work/gacm"},
        "ending_repository": {"sha": END, "repository_id": "repo-gacm", "branch": "main", "worktree": "C:/work/gacm"},
        "actual_changed_paths": ("src/local.py",),
        "diff_evidence": {"source": "git", "base": START, "head": END},
        "test_contract": ("test-local",),
        "test_outcomes": {"test-local": {"status": "PASS", "runner": "unittest", "result_digest": "c" * 64, "candidate_sha": END}},
        "allowed_writable_surfaces": ("src/*",),
        "forbidden_surfaces": ("schemas/*", "CURRENT_STATE.md"),
        "operational_context": {"status": "VERIFIED", "context_id": "ctx-1", "context_revision": "1"},
        "routing_decision": {"decision_id": "route-1", "selected_model": "gpt-5.6-luna", "qualification_identity": "qual-luna-1"},
        "broader_requalification_triggers": ("ARCHITECTURE", "SHARED_AUTHORITY", "MODEL_BEARING"),
        "claimed_affected_scope": ("src/local.py",),
        "prior_assurance": (
            {"assurance_id": "assure-local", "surfaces": ("src/local.py",), "depends_on": (), "rerun_scope": ("test-local",)},
            {"assurance_id": "assure-other", "surfaces": ("src/other.py",), "depends_on": (), "rerun_scope": ("test-other",)},
        ),
        "scope_patterns": {"authority": ("CURRENT_STATE.md",), "model": ("prompts/*",), "architecture": ("schemas/*",)},
        "dependency_paths": ("src/dependencies/*",),
        "expected_outcome_met": True,
    }
    values.update(overrides)
    return VerificationInput(**values)


class IndependentVerificationTests(unittest.TestCase):
    def setUp(self):
        self.engine = IndependentVerificationEngine(clock=lambda: "2026-09-14T15:00:00Z")

    def test_valid_complete_evidence_passes(self):
        receipt = self.engine.verify(base_input())
        self.assertEqual("PASS", receipt.status)
        self.assertTrue(receipt.authoritative)
        self.assertEqual("INDEPENDENT_VERIFIER", receipt.issuer_role)

    def test_unauthorized_path_change_fails(self):
        result = self.engine.verify(base_input(actual_changed_paths=("docs/unapproved.md",)))
        self.assertEqual("FAIL", result.status)

    def test_starting_sha_mismatch_fails(self):
        result = self.engine.verify(base_input(starting_repository={"sha": END, "repository_id": "repo-gacm", "branch": "main", "worktree": "C:/work/gacm"}))
        self.assertEqual("FAIL", result.status)

    def test_ending_sha_mismatch_fails(self):
        result = self.engine.verify(base_input(ending_repository={"sha": START, "repository_id": "repo-gacm", "branch": "main", "worktree": "C:/work/gacm"}))
        self.assertEqual("FAIL", result.status)

    def test_missing_critical_evidence_is_unobservable(self):
        result = self.engine.verify(base_input(actual_changed_paths=None, diff_evidence=None))
        self.assertEqual("UNOBSERVABLE", result.status)

    def test_wrong_operational_context_fails(self):
        result = self.engine.verify(base_input(operational_context={"status": "VERIFIED", "context_id": "ctx-other", "context_revision": "1"}))
        self.assertEqual("FAIL", result.status)

    def test_wrong_routing_decision_or_model_fails(self):
        result = self.engine.verify(base_input(routing_decision={"decision_id": "route-other", "selected_model": "gpt-5.6-sol", "qualification_identity": "qual-other"}))
        self.assertEqual("FAIL", result.status)

    def test_executor_claimed_pass_but_evidence_fails(self):
        receipt = dict(base_input().execution_receipt)
        receipt["authoritative_pass"] = True
        result = self.engine.verify(base_input(execution_receipt=receipt, test_outcomes={"test-local": {"status": "FAIL", "runner": "unittest", "result_digest": "c" * 64, "candidate_sha": END}}))
        self.assertEqual("FAIL", result.status)
        self.assertFalse(result.authoritative)

    def test_noncompleted_execution_cannot_pass(self):
        receipt = dict(base_input().execution_receipt)
        receipt["execution_status"] = "FAILED"
        result = self.engine.verify(base_input(execution_receipt=receipt))
        self.assertEqual("FAIL", result.status)

    def test_git_diff_detects_executor_omission(self):
        receipt = dict(base_input().execution_receipt)
        receipt["files_changed"] = ["src/local.py"]
        result = self.engine.verify(base_input(execution_receipt=receipt, actual_changed_paths=("src/local.py", "src/omitted.py")))
        self.assertEqual("FAIL", result.status)
        self.assertTrue(any("disagrees" in reason for reason in result.reasons))

    def test_git_diff_reader_recalculates_changed_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "GACM Test"], cwd=repo, check=True)
            (repo / "tracked.txt").write_text("one\n", encoding="utf-8")
            subprocess.run(["git", "add", "tracked.txt"], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-qm", "one"], cwd=repo, check=True)
            first = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
            (repo / "tracked.txt").write_text("two\n", encoding="utf-8")
            (repo / "omitted.txt").write_text("new\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-qm", "two"], cwd=repo, check=True)
            second = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
            paths, evidence = GitDiffEvidenceReader(repo).read(first, second)
            self.assertEqual(("omitted.txt", "tracked.txt"), paths)
            self.assertEqual(first, evidence["base"])
            self.assertEqual(second, evidence["head"])

    def test_local_repair_preserves_unrelated_assurance(self):
        result = self.engine.verify(base_input())
        self.assertEqual("LOCAL", result.affected_scope_determination["classification"])
        self.assertIn("assure-other", result.prior_assurance_preserved)
        self.assertNotIn("assure-other", result.prior_assurance_invalidated)
        self.assertFalse(result.broader_requalification_required)

    def test_dependency_change_expands_verification_scope(self):
        result = self.engine.verify(base_input(actual_changed_paths=("src/dependencies/lib.py",)))
        self.assertEqual("DEPENDENCY_EXPANDED", result.affected_scope_determination["classification"])
        self.assertTrue(result.broader_requalification_required)

    def test_authority_change_invalidates_authority_assurance(self):
        assurance = ({"assurance_id": "assure-authority", "surfaces": ("CURRENT_STATE.md",), "depends_on": ("authority",), "rerun_scope": ("authority-check",)},)
        result = self.engine.verify(base_input(actual_changed_paths=("CURRENT_STATE.md",), allowed_writable_surfaces=("*",), prior_assurance=assurance))
        self.assertEqual("AUTHORITY_BEARING", result.affected_scope_determination["classification"])
        self.assertIn("assure-authority", result.prior_assurance_invalidated)

    def test_model_change_requires_requalification(self):
        result = self.engine.verify(base_input(actual_changed_paths=("prompts/router.txt",), allowed_writable_surfaces=("*",)))
        self.assertEqual("MODEL_BEARING", result.affected_scope_determination["classification"])
        self.assertTrue(result.broader_requalification_required)

    def test_architecture_change_requires_broader_requalification(self):
        result = self.engine.verify(base_input(actual_changed_paths=("schemas/new.json",), allowed_writable_surfaces=("*",)))
        self.assertEqual("ARCHITECTURE_BEARING", result.affected_scope_determination["classification"])
        self.assertTrue(result.broader_requalification_required)

    def test_unknown_blast_radius_is_blocked(self):
        result = self.engine.verify(base_input(actual_changed_paths=()))
        self.assertEqual("BLOCKED", result.status)
        self.assertEqual("UNKNOWN", result.affected_scope_determination["classification"])

    def test_receipt_projects_into_phase_two_state(self):
        receipt = self.engine.verify(base_input())
        projection = receipt.to_run_state_projection()
        state = json.loads((ROOT / "tests" / "fixtures" / "valid_multi_unit_running.json").read_text(encoding="utf-8"))
        state["evidence"].append(projection["evidence"])
        state["work_units"][1].update({
            "status": projection["work_unit"]["status"],
            "verification": projection["work_unit"]["verification"],
            "affected_scope": projection["work_unit"]["affected_scope"],
            "broader_requalification_triggers": [],
            "output_evidence": projection["work_unit"]["output_evidence"],
        })
        schema = json.loads((ROOT / "schemas" / "gacm-run-state.schema.json").read_text(encoding="utf-8"))
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(state))
        self.assertEqual([], errors)

    def test_only_verifier_can_set_authoritative_pass(self):
        receipt = self.engine.verify(base_input())
        self.assertTrue(receipt.authoritative)
        self.assertEqual("INDEPENDENT_VERIFIER", receipt.issuer_role)
        self.assertTrue(receipt.to_run_state_projection()["work_unit"]["verification"]["authoritative"])

    def test_executor_pass_receipt_is_rejected(self):
        executor_pass = dict(base_input().execution_receipt)
        executor_pass["verification"] = {"status": "PASS", "authoritative": True, "issuer_role": "EXECUTOR"}
        result = self.engine.verify(base_input(execution_receipt=executor_pass))
        self.assertEqual("FAIL", result.status)

    def test_identical_evidence_is_deterministic(self):
        first = self.engine.verify(base_input()).to_dict()
        second = self.engine.verify(base_input()).to_dict()
        self.assertEqual(first, second)

    def test_regression_failure_is_detected(self):
        result = self.engine.verify(base_input(test_outcomes={"test-local": {"status": "FAIL", "runner": "unittest", "result_digest": "c" * 64, "candidate_sha": END}}))
        self.assertEqual("FAIL", result.status)
        self.assertEqual("FAIL", result.regression_result)

    def test_missing_test_outcome_is_unobservable(self):
        result = self.engine.verify(base_input(test_outcomes={}))
        self.assertEqual("UNOBSERVABLE", result.status)

    def test_expected_outcome_failure_is_detected(self):
        result = self.engine.verify(base_input(expected_outcome_met=False))
        self.assertEqual("FAIL", result.status)

    def test_unset_expected_outcome_holds(self):
        result = self.engine.verify(base_input(expected_outcome_met=None))
        self.assertEqual("UNOBSERVABLE", result.status)

    def test_test_outcome_without_provenance_is_unobservable(self):
        result = self.engine.verify(base_input(test_outcomes={"test-local": "PASS"}))
        self.assertEqual("UNOBSERVABLE", result.status)

    def test_stale_test_outcome_candidate_is_unobservable(self):
        outcome = {"status": "PASS", "runner": "unittest", "result_digest": "c" * 64, "candidate_sha": START}
        result = self.engine.verify(base_input(test_outcomes={"test-local": outcome}))
        self.assertEqual("UNOBSERVABLE", result.status)


if __name__ == "__main__":
    unittest.main()
