import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gacm.routing import (  # noqa: E402
    CapabilityClass,
    DeterministicModelRouter,
    ModelQualification,
    ModelRegistry,
    RoutingBlocked,
    WorkUnit,
    default_pilot_registry,
)


def dimensions(**overrides):
    values = {name: 0 for name in (
        "task_complexity", "ambiguity", "blast_radius", "architectural_impact",
        "authority_sensitivity", "security_sensitivity", "reasoning_depth",
        "repair_complexity", "verification_complexity",
    )}
    values.update(overrides)
    return values


class ModelRouterTests(unittest.TestCase):
    def setUp(self):
        self.router = DeterministicModelRouter(default_pilot_registry(), clock=lambda: "2026-09-14T15:00:00Z")

    def test_mechanical_bounded_task_selects_luna(self):
        decision = self.router.route(WorkUnit("WU-LUNA", dimensions(task_complexity=1)))
        self.assertEqual("gpt-5.6-luna", decision.selected_model)
        self.assertEqual("mechanical", decision.selected_model_class)

    def test_precision_sensitive_task_selects_terra(self):
        decision = self.router.route(WorkUnit("WU-TERRA", dimensions(reasoning_depth=2)))
        self.assertEqual("gpt-5.6-terra", decision.selected_model)
        self.assertEqual("precision", decision.selected_model_class)

    def test_architecture_high_risk_task_selects_sol(self):
        decision = self.router.route(WorkUnit("WU-SOL", dimensions(architectural_impact=3)))
        self.assertEqual("gpt-5.6-sol", decision.selected_model)
        self.assertEqual("architecture", decision.selected_model_class)

    def test_security_sensitive_task_requires_architecture_class(self):
        decision = self.router.route(WorkUnit("WU-SECURITY", dimensions(security_sensitivity=3)))
        self.assertEqual(CapabilityClass.ARCHITECTURE.name.lower(), decision.selected_model_class)

    def test_authority_sensitive_task_requires_architecture_class(self):
        decision = self.router.route(WorkUnit("WU-AUTHORITY", dimensions(authority_sensitivity=3)))
        self.assertEqual("gpt-5.6-sol", decision.selected_model)

    def test_cheaper_underqualified_model_cannot_win(self):
        registry = ModelRegistry((
            ModelQualification("cheap-luna", CapabilityClass.MECHANICAL, "p", "qual-cheap", 4, 0),
            ModelQualification("qualified-terra", CapabilityClass.PRECISION, "p", "qual-terra", 2, 2),
        ))
        decision = DeterministicModelRouter(registry, clock=lambda: "2026-09-14T15:00:00Z").route(
            WorkUnit("WU-COST", dimensions(task_complexity=2))
        )
        self.assertEqual("qualified-terra", decision.selected_model)

    def test_unqualified_registry_entry_cannot_be_selected(self):
        registry = ModelRegistry((ModelQualification("luna", CapabilityClass.MECHANICAL, "p", "qual", 1, 1, False),))
        with self.assertRaises(RoutingBlocked):
            DeterministicModelRouter(registry).route(WorkUnit("WU-UNQUALIFIED", dimensions()))

    def test_no_qualified_model_is_blocked(self):
        registry = ModelRegistry((ModelQualification("terra", CapabilityClass.PRECISION, "p", "qual", 2, 1),))
        with self.assertRaises(RoutingBlocked):
            DeterministicModelRouter(registry).route(WorkUnit("WU-BLOCKED", dimensions(security_sensitivity=3)))

    def test_escalation_preserves_original_decision(self):
        decision = self.router.route(WorkUnit("WU-ESCALATE", dimensions(task_complexity=1)))
        escalated = self.router.escalate(WorkUnit("WU-ESCALATE", dimensions(task_complexity=3)), decision)
        self.assertEqual("gpt-5.6-luna", decision.selected_model)
        self.assertEqual("gpt-5.6-sol", escalated.selected_model)
        self.assertTrue(escalated.escalation_required)
        self.assertEqual(decision.decision_id, escalated.supersedes_decision_id)
        self.assertNotEqual(decision.decision_id, escalated.decision_id)
        projected = escalated.to_run_state_model((decision,))
        self.assertEqual(
            [decision.decision_id, escalated.decision_id],
            [item["decision_id"] for item in projected["routing_history"]],
        )

    def test_execution_model_cannot_override_route(self):
        work_unit = WorkUnit("WU-NO-OVERRIDE", dimensions(reasoning_depth=2))
        self.assertEqual(
            self.router.route(work_unit).to_dict(),
            self.router.route(work_unit, execution_model="gpt-5.6-sol").to_dict(),
        )

    def test_routing_decision_projects_into_phase_two_run_state(self):
        decision = self.router.route(WorkUnit("WU-STATE", dimensions(task_complexity=1)))
        model = decision.to_run_state_model()
        state = json.loads((ROOT / "tests" / "fixtures" / "valid_new_run.json").read_text(encoding="utf-8"))
        state["work_units"][0]["model"] = model
        schema = json.loads((ROOT / "schemas" / "gacm-run-state.schema.json").read_text(encoding="utf-8"))
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(state))
        self.assertEqual([], errors)

    def test_routing_decision_cannot_create_authoritative_pass(self):
        decision = self.router.route(WorkUnit("WU-NO-PASS", dimensions()))
        projected = decision.to_run_state_model()
        self.assertNotIn("verification", projected)
        self.assertNotIn("authoritative_pass", projected)
        self.assertNotEqual("PASS", projected.get("status"))

    def test_identical_inputs_are_deterministic_with_same_clock(self):
        unit = WorkUnit("WU-DETERMINISTIC", dimensions(ambiguity=2))
        first = self.router.route(unit).to_dict()
        second = self.router.route(unit).to_dict()
        self.assertEqual(first, second)

    def test_cost_breaks_only_capability_equivalent_tie(self):
        registry = ModelRegistry((
            ModelQualification("terra-expensive", CapabilityClass.PRECISION, "p", "qual-expensive", 2, 5),
            ModelQualification("terra-cheap", CapabilityClass.PRECISION, "p", "qual-cheap", 2, 1),
            ModelQualification("sol-cheapest", CapabilityClass.ARCHITECTURE, "p", "qual-sol", 4, 0),
        ))
        decision = DeterministicModelRouter(registry, clock=lambda: "2026-09-14T15:00:00Z").route(
            WorkUnit("WU-TIE", dimensions(ambiguity=2))
        )
        self.assertEqual("terra-cheap", decision.selected_model)

    def test_escalation_without_higher_qualified_class_is_blocked(self):
        decision = self.router.route(WorkUnit("WU-AT-SOL", dimensions(security_sensitivity=3)))
        with self.assertRaises(RoutingBlocked):
            self.router.escalate(WorkUnit("WU-AT-SOL", dimensions(security_sensitivity=3)), decision)


if __name__ == "__main__":
    unittest.main()
