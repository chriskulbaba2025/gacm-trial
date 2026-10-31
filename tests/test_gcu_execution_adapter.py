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
    ProposedAction,
    RunnerResult,
    WorkUnitContract,
    recipe_digest,
)


SHA = "a" * 40
END_SHA = "b" * 40


def frozen_recipe(work_unit_id="unit-exec"):
    return {
        "schema": "GACM_EXECUTION_RECIPE_V1",
        "recipe_id": "recipe-" + work_unit_id,
        "version": "1",
        "state": "FROZEN",
        "work_unit_id": work_unit_id,
        "mutation_policy": "GOVERNED_REFREEZE_REQUIRED",
        "steps": [{
            "step_id": "step-1",
            "sequence": 1,
            "allowed_actions": [{
                "action_kind": "COMMAND",
                "tools": ["python", "deploy"],
                "target_patterns": ["work-unit"],
                "parameter_constraints": {
                    "allowed_keys": ["command"],
                    "required_keys": ["command"],
                    "string_prefixes": {"command": ["python -m unittest", "deploy --account"]},
                },
                "judgment_slot_id": None,
            }],
            "bounded_judgment_slots": [],
            "acceptable_prior_states": ["EXECUTION"],
            "expected_result_states": ["DONE"],
            "evidence_requirements": ["action receipt"],
            "stop_conditions": ["authority mismatch", "unexpected state"],
        }],
    }


class StaticGuardedRunner:
    def __init__(self, result):
        self.result = result

    def run(self, package, authority_gate):
        command = self.result.commands_executed[0] if self.result.commands_executed else "python -m unittest"
        tool = "deploy" if command.startswith("deploy ") else "python"
        action = ProposedAction(
            action_id="action-1", step_id="step-1", action_kind="COMMAND",
            tool=tool, target="work-unit", parameters={"command": command},
        )
        decision = authority_gate.authorize(action, "EXECUTION")
        if decision.result != "ALLOW":
            return RunnerResult(ending_sha=None, status="BLOCKED", stop_reason=decision.reason)
        authority_gate.record_result("action-1", "DONE", ("evidence:action-1",))
        return self.result


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
        "graph_action_id": "graph-action-1",
        "graph_revision": 7,
        "graph_target_object_id": "tranche-1",
        "graph_project_id": "project-gacm",
        "external_action_required": False,
        "allowed_writable_paths": ("src/gacm/execution/*",),
        "forbidden_paths": ("CURRENT_STATE.md", "schemas/*"),
        "test_contract": ("python -m unittest",),
        "evidence_requirements": ("receipt", "diff", "test-output"),
        "stop_conditions": ("authority mismatch", "scope violation"),
        "broader_requalification_triggers": ("ARCHITECTURE", "SHARED_SCHEMA"),
        "execution_recipe": frozen_recipe("unit-exec"),
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
        "current_state": {
            "work_unit_status": "READY",
            "head": SHA,
            "branch": "main",
            "worktree": "C:/work/gacm",
            "clean": True,
            "graph_action_id": "graph-action-1",
            "graph_revision": 7,
            "graph_target_object_id": "tranche-1",
            "graph_project_id": "project-gacm",
            "execution_authority_state": "EXECUTION",
            "execution_recipe_digest": recipe_digest(c.execution_recipe),
        },
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
    return StaticGuardedRunner(RunnerResult(**values))


class GCUExecutionAdapterTests(unittest.TestCase):
    def setUp(self):
        self.clock_values = iter(("2026-09-14T15:00:00Z", "2026-09-14T15:01:00Z"))
        self.adapter = GCUExecutionAdapter(clock=lambda: next(self.clock_values))

    def test_valid_ready_work_unit_produces_execution_package(self):
        package = self.adapter.prepare(request())
        self.assertEqual("READY", package.status)
        self.assertTrue(package.package_id.startswith("pkg-"))
        self.assertIn("machine_policy", package.rendered_prompt)

    def test_machine_policy_contains_exact_graph_binding(self):
        package = self.adapter.prepare(request())
        binding = package.machine_policy["contract"]["graph_binding"]
        self.assertEqual("graph-action-1", binding["graph_action_id"])
        self.assertEqual(7, binding["graph_revision"])
        self.assertEqual("tranche-1", binding["target_object_id"])
        self.assertEqual("project-gacm", binding["project_id"])

    def test_graph_revision_mismatch_is_blocked(self):
        package = self.adapter.prepare(request(contract=contract(graph_revision=8)))
        self.assertEqual("BLOCKED", package.status)
        self.assertIn("graph revision", " ".join(package.blocking_reasons))

    def test_graph_action_mismatch_is_blocked(self):
        package = self.adapter.prepare(
            request(contract=contract(graph_action_id="graph-action-other"))
        )
        self.assertEqual("BLOCKED", package.status)
        self.assertIn("graph action", " ".join(package.blocking_reasons))

    def test_routing_decision_identity_mismatch_is_blocked(self):
        package = self.adapter.prepare(
            request(
                routing_decision={
                    "decision_id": "route-other",
                    "selected_model": "gpt-5.6-luna",
                    "qualification_identity": "qual-luna-1",
                }
            )
        )
        self.assertEqual("BLOCKED", package.status)
        self.assertIn("routing decision identity", " ".join(package.blocking_reasons))

    def test_non_luna_route_requires_durable_human_authorization(self):
        terra_contract = contract(
            selected_model="gpt-5.6-terra",
            qualification_identity="qual-terra-1",
            routing_decision_id="route-terra",
        )
        route = {
            "decision_id": "route-terra",
            "selected_model": "gpt-5.6-terra",
            "qualification_identity": "qual-terra-1",
        }
        package = self.adapter.prepare(
            request(contract=terra_contract, routing_decision=route)
        )
        self.assertEqual("BLOCKED", package.status)
        self.assertIn("human authorization", " ".join(package.blocking_reasons))

        route["human_authorization_id"] = "human-terra-1"
        route["model_authority_ref"] = "human://chris/model-authorization"
        package = self.adapter.prepare(
            request(contract=terra_contract, routing_decision=route)
        )
        self.assertEqual("READY", package.status)

    def test_graph_revision_changes_execution_package_identity(self):
        first_request = request()
        first = self.adapter.prepare(first_request)
        current = dict(first_request.current_state)
        current["graph_revision"] = 8
        second_contract = contract(graph_revision=8)
        current["execution_recipe_digest"] = recipe_digest(second_contract.execution_recipe)
        second = self.adapter.prepare(
            request(
                contract=second_contract,
                current_state=current,
            )
        )
        self.assertEqual("READY", second.status)
        self.assertNotEqual(first.package_id, second.package_id)


    def test_execution_recipe_digest_mismatch_is_blocked(self):
        req = request()
        state = dict(req.current_state)
        state["execution_recipe_digest"] = "0" * 64
        package = self.adapter.prepare(request(current_state=state))
        self.assertEqual("BLOCKED", package.status)
        self.assertIn("execution recipe digest", " ".join(package.blocking_reasons))

    def test_execution_authority_state_must_be_explicit_execution(self):
        req = request()
        state = dict(req.current_state)
        state["execution_authority_state"] = "DESIGN"
        package = self.adapter.prepare(request(current_state=state))
        self.assertEqual("BLOCKED", package.status)
        self.assertIn("execution authority state", " ".join(package.blocking_reasons))

    def test_unguarded_runner_is_blocked_before_executor_invocation(self):
        called = []
        def legacy_runner(package):
            called.append(package)
            return RunnerResult(ending_sha=END_SHA)
        receipt = self.adapter.execute(request(), legacy_runner)
        self.assertEqual("BLOCKED", receipt.execution_status)
        self.assertFalse(called)
        self.assertIn("per-action authorization", receipt.stop_reason)

    def test_action_authorization_receipt_is_preserved(self):
        receipt = self.adapter.execute(request(), completed_runner())
        action_receipts = [
            item for item in receipt.evidence_artifacts
            if item.get("kind") == "ACTION_AUTHORIZATION_RECEIPT"
        ]
        self.assertEqual(1, len(action_receipts))
        self.assertTrue(action_receipts[0]["complete"])
        self.assertEqual("VERIFICATION", action_receipts[0]["final_authority_state"])

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
        receipt = self.adapter.execute(request(), StaticGuardedRunner(result))
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
