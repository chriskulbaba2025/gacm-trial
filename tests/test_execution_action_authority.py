import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gacm.execution import (  # noqa: E402
    ActionAuthorizationGate,
    ActionAuthorityError,
    ProposedAction,
    recipe_digest,
    validate_recipe,
)


def recipe():
    return {
        "schema": "GACM_EXECUTION_RECIPE_V1",
        "recipe_id": "recipe-unit-a",
        "version": "1",
        "state": "FROZEN",
        "work_unit_id": "unit-a",
        "mutation_policy": "GOVERNED_REFREEZE_REQUIRED",
        "steps": [
            {
                "step_id": "inspect",
                "sequence": 1,
                "allowed_actions": [{
                    "action_kind": "READ",
                    "tools": ["git"],
                    "target_patterns": ["repo/*"],
                    "parameter_constraints": {
                        "allowed_keys": ["command"],
                        "required_keys": ["command"],
                        "exact": {"command": "git status --porcelain"},
                    },
                    "judgment_slot_id": None,
                }],
                "bounded_judgment_slots": [],
                "acceptable_prior_states": ["EXECUTION"],
                "expected_result_states": ["INSPECTED"],
                "evidence_requirements": ["status receipt"],
                "stop_conditions": ["worktree dirty"],
            },
            {
                "step_id": "choose",
                "sequence": 2,
                "allowed_actions": [{
                    "action_kind": "CLASSIFY",
                    "tools": ["gacm"],
                    "target_patterns": ["finding/*"],
                    "parameter_constraints": {
                        "allowed_keys": ["candidate_count"],
                        "required_keys": ["candidate_count"],
                        "allowed_values": {"candidate_count": [2]},
                    },
                    "judgment_slot_id": "slot-class",
                }],
                "bounded_judgment_slots": [{
                    "slot_id": "slot-class",
                    "purpose": "Choose one already-authorized classification",
                    "allowed_values": ["A", "B"],
                    "may_expand_scope": False,
                }],
                "acceptable_prior_states": ["EXECUTION"],
                "expected_result_states": ["CLASSIFIED"],
                "evidence_requirements": ["classification receipt"],
                "stop_conditions": ["candidate set changed"],
            },
        ],
    }


class ActionAuthorityTests(unittest.TestCase):
    def test_exact_actions_advance_only_through_frozen_sequence(self):
        gate = ActionAuthorizationGate(recipe(), "unit-a")
        first = ProposedAction(
            "a1", "inspect", "READ", "git", "repo/current",
            {"command": "git status --porcelain"},
        )
        decision = gate.authorize(first, "EXECUTION")
        self.assertEqual("ALLOW", decision.result)
        gate.record_result("a1", "INSPECTED", ("ev-status",))
        self.assertEqual("choose", gate.current_step["step_id"])

        second = ProposedAction(
            "a2", "choose", "CLASSIFY", "gacm", "finding/7",
            {"candidate_count": 2}, "slot-class", "A",
        )
        self.assertEqual("ALLOW", gate.authorize(second, "EXECUTION").result)
        gate.record_result("a2", "CLASSIFIED", ("ev-class",))
        self.assertTrue(gate.complete())
        self.assertEqual("VERIFICATION", gate.state)
        evidence = gate.evidence()
        self.assertEqual(2, len(evidence["decisions"]))
        self.assertEqual(2, len(evidence["transitions"]))

    def test_out_of_sequence_action_fails_closed(self):
        gate = ActionAuthorizationGate(recipe(), "unit-a")
        action = ProposedAction(
            "a2", "choose", "CLASSIFY", "gacm", "finding/7",
            {"candidate_count": 2}, "slot-class", "A",
        )
        decision = gate.authorize(action, "EXECUTION")
        self.assertEqual("DENY", decision.result)
        self.assertEqual("BLOCKED", gate.state)

    def test_available_but_unauthorized_tool_does_not_create_authority(self):
        gate = ActionAuthorizationGate(recipe(), "unit-a")
        action = ProposedAction(
            "a1", "inspect", "READ", "powershell", "repo/current",
            {"command": "git status --porcelain"},
        )
        self.assertEqual("DENY", gate.authorize(action, "EXECUTION").result)
        self.assertEqual("BLOCKED", gate.state)

    def test_parameter_or_target_workaround_is_denied(self):
        for action in (
            ProposedAction("a1", "inspect", "READ", "git", "other/current", {"command": "git status --porcelain"}),
            ProposedAction("a1", "inspect", "READ", "git", "repo/current", {"command": "git reset --hard"}),
            ProposedAction("a1", "inspect", "READ", "git", "repo/current", {"command": "git status --porcelain", "force": True}),
        ):
            gate = ActionAuthorizationGate(recipe(), "unit-a")
            self.assertEqual("DENY", gate.authorize(action, "EXECUTION").result)
            self.assertEqual("BLOCKED", gate.state)

    def test_bounded_judgment_is_limited_to_declared_slot_and_values(self):
        gate = ActionAuthorizationGate(recipe(), "unit-a")
        gate.authorize(
            ProposedAction("a1", "inspect", "READ", "git", "repo/current", {"command": "git status --porcelain"}),
            "EXECUTION",
        )
        gate.record_result("a1", "INSPECTED", ("ev",))
        bad = ProposedAction(
            "a2", "choose", "CLASSIFY", "gacm", "finding/7",
            {"candidate_count": 2}, "slot-class", "C",
        )
        self.assertEqual("DENY", gate.authorize(bad, "EXECUTION").result)

    def test_unbounded_judgment_on_non_judgment_action_is_denied(self):
        gate = ActionAuthorizationGate(recipe(), "unit-a")
        action = ProposedAction(
            "a1", "inspect", "READ", "git", "repo/current",
            {"command": "git status --porcelain"}, "slot-class", "A",
        )
        self.assertEqual("DENY", gate.authorize(action, "EXECUTION").result)

    def test_result_transition_requires_authorized_state_and_evidence(self):
        gate = ActionAuthorizationGate(recipe(), "unit-a")
        gate.authorize(
            ProposedAction("a1", "inspect", "READ", "git", "repo/current", {"command": "git status --porcelain"}),
            "EXECUTION",
        )
        with self.assertRaises(ActionAuthorityError):
            gate.record_result("a1", "WRONG_STATE", ("ev",))
        self.assertEqual("BLOCKED", gate.state)

        gate = ActionAuthorizationGate(recipe(), "unit-a")
        gate.authorize(
            ProposedAction("a1", "inspect", "READ", "git", "repo/current", {"command": "git status --porcelain"}),
            "EXECUTION",
        )
        with self.assertRaises(ActionAuthorityError):
            gate.record_result("a1", "INSPECTED", ())
        self.assertEqual("BLOCKED", gate.state)

    def test_original_recipe_mutation_cannot_expand_live_gate(self):
        original = recipe()
        gate = ActionAuthorizationGate(original, "unit-a")
        frozen_digest = gate.recipe_digest
        original["steps"][0]["allowed_actions"][0]["tools"].append("powershell")
        self.assertNotEqual(frozen_digest, recipe_digest(original))
        action = ProposedAction(
            "a1", "inspect", "READ", "powershell", "repo/current",
            {"command": "git status --porcelain"},
        )
        self.assertEqual("DENY", gate.authorize(action, "EXECUTION").result)

    def test_recipe_must_be_frozen_and_self_mutation_policy_forbidden(self):
        unfrozen = recipe()
        unfrozen["state"] = "DESIGN"
        with self.assertRaises(ActionAuthorityError):
            validate_recipe(unfrozen, "unit-a")
        mutable = recipe()
        mutable["mutation_policy"] = "EXECUTOR_MAY_EDIT"
        with self.assertRaises(ActionAuthorityError):
            validate_recipe(mutable, "unit-a")


if __name__ == "__main__":
    unittest.main()
