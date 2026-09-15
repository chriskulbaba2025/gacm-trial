import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gacm.execution import (  # noqa: E402
    ExecutionRequest,
    GCUExecutionAdapter,
    RunnerResult,
    WorkUnitContract,
)


SHA = "a" * 40
END_SHA = "b" * 40


def contract(**overrides):
    values = {
        "run_id": "run-exec",
        "work_unit_id": "unit-exec",
        "task_objective": "make bounded change",
        "expected_outcome": "the bounded change is implemented",
        "repository_id": "repo-gacm",
        "authorized_start_sha": SHA,
        "branch": "main",
        "worktree": "C:/work/gacm",
        "context_snapshot_id": "ctx-1",
        "context_snapshot_revision": "1",
        "selected_model": "gpt-5.6-luna",
        "qualification_identity": "qual-luna-1",
        "allowed_writable_paths": ("src/gacm/execution/*",),
        "forbidden_paths": ("CURRENT_STATE.md", "schemas/*"),
        "test_contract": ("python -m unittest",),
        "evidence_requirements": ("receipt", "diff", "test-output"),
        "stop_conditions": ("authority mismatch", "scope violation"),
        "broader_requalification_triggers": ("ARCHITECTURE", "SHARED_SCHEMA"),
        "routing_decision_id": "route-1",
        "rollback_authority": "rollback-sha-1",
    }
    values.update(overrides)
    return WorkUnitContract(**values)


def request(**overrides):
    c = overrides.pop("contract", contract())
    values = {
        "contract": c,
        "authority": {"status": "VERIFIED", "repository_id": "repo-gacm", "branch": "main", "worktree": "C:/work/gacm", "head": SHA},
        "operational_context": {"status": "VERIFIED", "context_id": "ctx-1", "context_revision": "1"},
        "routing_decision": {"decision_id": "route-1", "selected_model": "gpt-5.6-luna", "qualification_identity": "qual-luna-1"},
        "current_state": {"work_unit_status": "READY", "head": SHA, "branch": "main", "worktree": "C:/work/gacm", "clean": True},
        "category_patterns": {"authority": ("CURRENT_STATE.md",), "model": ("prompts/*",), "architecture": ("schemas/*",)},
    }
    values.update(overrides)
    return ExecutionRequest(**values)


def completed_runner(files=("src/gacm/execution/adapter.py",), **overrides):
    values = {
        "ending_sha": END_SHA,
        "files_changed": tuple(files),
        "commands_executed": ("python -m unittest",),
        "tests_executed": ("python -m unittest",),
        "test_outcomes": {"python -m unittest": "PASS"},
        "evidence_artifacts": ({"path": "evidence/test.txt", "sha": "c" * 64},),
        "claimed_affected_scope": ("src/gacm/execution/adapter.py",),
        "model_used": "gpt-5.6-luna",
        "starting_sha": SHA,
        "status": "COMPLETED",
    }
    values.update(overrides)
    return lambda package: RunnerResult(**values)


class GCUExecutionAdapterTests(unittest.TestCase):
    def setUp(self):
        self.clock_values = iter(("2026-09-14T15:00:00Z", "2026-09-14T15:01:00Z"))
        self.adapter = GCUExecutionAdapter(clock=lambda: next(self.clock_values))

    def test_valid_ready_work_unit_produces_execution_package(self):
        package = self.adapter.prepare(request())
        self.assertEqual("READY", package.status)
        self.assertTrue(package.package_id.startswith("pkg-"))
        self.assertIn("machine_policy", package.rendered_prompt)

    def test_unverified_github_authority_is_blocked(self):
        package = self.adapter.prepare(request(authority={"status": "BLOCKED"}))
        self.assertEqual("BLOCKED", package.status)
        self.assertIn("GitHub authority", " ".join(package.blocking_reasons))

    def test_unverified_context_is_blocked(self):
        package = self.adapter.prepare(request(operational_context={"status": "AMBIGUOUS", "context_id": "ctx-1", "context_revision": "1"}))
        self.assertEqual("BLOCKED", package.status)

    def test_missing_routing_decision_is_blocked(self):
        package = self.adapter.prepare(request(routing_decision={}))
        self.assertEqual("BLOCKED", package.status)

    def test_unqualified_model_is_blocked(self):
        package = self.adapter.prepare(request(contract=contract(model_qualified=False)))
        self.assertEqual("BLOCKED", package.status)

    def test_starting_sha_mismatch_is_blocked(self):
        package = self.adapter.prepare(request(current_state={"work_unit_status": "READY", "head": END_SHA, "branch": "main", "worktree": "C:/work/gacm", "clean": True}))
        self.assertEqual("BLOCKED", package.status)

    def test_wrong_branch_and_worktree_are_blocked(self):
        package = self.adapter.prepare(request(current_state={"work_unit_status": "READY", "head": SHA, "branch": "other", "worktree": "C:/other", "clean": True}))
        self.assertEqual("BLOCKED", package.status)

    def test_unauthorized_changed_path_fails_and_preserves_evidence(self):
        receipt = self.adapter.execute(request(), completed_runner(files=("src/gacm/execution/adapter.py", "schemas/gacm-run-state.schema.json")))
        self.assertEqual("FAILED", receipt.execution_status)
        self.assertIn("schemas/gacm-run-state.schema.json", receipt.stop_reason)
        self.assertEqual(END_SHA, receipt.ending_sha)

    def test_authorized_changed_path_produces_non_authoritative_receipt(self):
        receipt = self.adapter.execute(request(), completed_runner())
        self.assertEqual("COMPLETED", receipt.execution_status)
        self.assertEqual(SHA, receipt.starting_sha)
        self.assertEqual(END_SHA, receipt.ending_sha)
        self.assertFalse(receipt.to_dict()["authoritative_pass"])

    def test_receipt_cannot_create_authoritative_pass(self):
        receipt = self.adapter.execute(request(), completed_runner())
        projection = receipt.to_run_state_projection()
        self.assertEqual("VERIFYING", projection["work_unit"]["status"])
        self.assertFalse(projection["work_unit"]["verification"]["authoritative"])
        self.assertNotEqual("PASS", projection["work_unit"]["verification"]["status"])

    def test_local_repair_evidence_does_not_invalidate_unrelated_pass(self):
        receipt = self.adapter.execute(request(), completed_runner())
        self.assertEqual({"authority": False, "model": False, "architecture": False}, dict(receipt.changed_surface_flags))
        self.assertEqual([], receipt.to_run_state_projection()["work_unit"].get("invalidated_units", []))

    def test_authority_model_architecture_surfaces_are_flagged(self):
        result = RunnerResult(
            ending_sha=END_SHA,
            files_changed=("CURRENT_STATE.md", "prompts/router.txt", "schemas/gacm-run-state.schema.json"),
            claimed_affected_scope=("CURRENT_STATE.md",),
            model_used="gpt-5.6-luna",
            starting_sha=SHA,
        )
        receipt = self.adapter.execute(request(), lambda package: result)
        self.assertEqual({"authority": True, "model": True, "architecture": True}, dict(receipt.changed_surface_flags))
        self.assertEqual("FAILED", receipt.execution_status)

    def test_projection_can_be_recorded_in_phase_two_state(self):
        receipt = self.adapter.execute(request(), completed_runner())
        state = json.loads((ROOT / "tests" / "fixtures" / "valid_multi_unit_running.json").read_text(encoding="utf-8"))
        projection = receipt.to_run_state_projection()
        state["evidence"].append(projection["evidence"])
        unit = state["work_units"][1]
        unit.update(projection["work_unit"])
        self.assertEqual("VERIFYING", unit["status"])
        self.assertEqual("EXECUTOR", state["evidence"][-1]["produced_by"])
        schema = json.loads((ROOT / "schemas" / "gacm-run-state.schema.json").read_text(encoding="utf-8"))
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(state))
        self.assertEqual([], errors)

    def test_identical_inputs_produce_identical_packages(self):
        first = self.adapter.prepare(request()).to_dict()
        second = self.adapter.prepare(request()).to_dict()
        self.assertEqual(first, second)

    def test_prompt_cannot_override_machine_policy(self):
        package = self.adapter.prepare(request())
        self.assertEqual(package.machine_policy["contract"]["selected_model"], "gpt-5.6-luna")
        self.assertIn("cannot expand scope", package.rendered_prompt)

    def test_executor_cannot_expand_writable_scope(self):
        receipt = self.adapter.execute(request(), completed_runner(files=("src/other/module.py",)))
        self.assertEqual("FAILED", receipt.execution_status)

    def test_executor_cannot_change_selected_model(self):
        receipt = self.adapter.execute(request(), completed_runner(model_used="gpt-5.6-sol"))
        self.assertEqual("FAILED", receipt.execution_status)
        self.assertIn("different from the authorized route", receipt.stop_reason)

    def test_execution_preserves_identity_and_evidence(self):
        receipt = self.adapter.execute(request(), completed_runner())
        data = receipt.to_dict()
        self.assertEqual(SHA, data["starting_sha"])
        self.assertEqual(END_SHA, data["ending_sha"])
        self.assertTrue(data["evidence_artifacts"])
        self.assertEqual("PASS", data["test_outcomes"]["python -m unittest"])

    def test_real_state_reader_is_checked_before_runner(self):
        class Reader:
            def read(self):
                return {"head": END_SHA, "branch": "main", "worktree": "C:/work/gacm", "clean": True}

        adapter = GCUExecutionAdapter(state_reader=Reader(), clock=lambda: "2026-09-14T15:00:00Z")
        called = []
        receipt = adapter.execute(request(), lambda package: called.append(package) or RunnerResult(ending_sha=END_SHA))
        self.assertEqual("BLOCKED", receipt.execution_status)
        self.assertFalse(called)


if __name__ == "__main__":
    unittest.main()
