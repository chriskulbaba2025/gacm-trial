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
    HumanModelAuthorizationRequired,
    ModelAuthorization,
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


def auth(work_unit_id, model_id, authorization_id="human-model-auth-1"):
    return ModelAuthorization(
        authorization_id=authorization_id,
        work_unit_id=work_unit_id,
        model_id=model_id,
        authority_ref="human://chris/explicit-model-authorization",
        actor_id="chris",
        authorized_at="2026-10-03T21:00:00Z",
    )


class ModelRouterTests(unittest.TestCase):
    def setUp(self):
        self.router = DeterministicModelRouter(
            default_pilot_registry(),
            clock=lambda: "2026-10-03T21:01:00Z",
        )

    def test_mechanical_bounded_task_selects_luna(self):
        decision = self.router.route(WorkUnit("WU-LUNA", dimensions(task_complexity=1)))
        self.assertEqual("gpt-5.6-luna", decision.selected_model)
        self.assertEqual("mechanical", decision.selected_model_class)
        self.assertIsNone(decision.human_authorization_id)
        self.assertIsNone(decision.model_authority_ref)

    def test_precision_task_does_not_auto_select_terra(self):
        with self.assertRaises(HumanModelAuthorizationRequired):
            self.router.route(WorkUnit("WU-TERRA", dimensions(reasoning_depth=2)))

    def test_architecture_task_does_not_auto_select_sol(self):
        with self.assertRaises(HumanModelAuthorizationRequired):
            self.router.route(WorkUnit("WU-SOL", dimensions(architectural_impact=3)))

    def test_human_authorization_can_select_terra(self):
        unit = WorkUnit("WU-TERRA-AUTH", dimensions(reasoning_depth=2))
        decision = self.router.route(
            unit,
            authorization=auth(unit.work_unit_id, "gpt-5.6-terra"),
        )
        self.assertEqual("gpt-5.6-terra", decision.selected_model)
        self.assertEqual("human-model-auth-1", decision.human_authorization_id)
        self.assertEqual(
            "human://chris/explicit-model-authorization",
            decision.model_authority_ref,
        )

    def test_human_authorization_can_select_sol(self):
        unit = WorkUnit("WU-SOL-AUTH", dimensions(security_sensitivity=3))
        decision = self.router.route(
            unit,
            authorization=auth(unit.work_unit_id, "gpt-5.6-sol"),
        )
        self.assertEqual("gpt-5.6-sol", decision.selected_model)
        self.assertEqual(CapabilityClass.ARCHITECTURE.name.lower(), decision.selected_model_class)

    def test_authorization_for_wrong_work_unit_is_blocked(self):
        unit = WorkUnit("WU-ONE", dimensions(reasoning_depth=2))
        with self.assertRaises(RoutingBlocked):
            self.router.route(
                unit,
                authorization=auth("WU-TWO", "gpt-5.6-terra"),
            )

    def test_authorized_underqualified_model_is_blocked(self):
        unit = WorkUnit("WU-HIGH", dimensions(security_sensitivity=3))
        with self.assertRaises(RoutingBlocked):
            self.router.route(
                unit,
                authorization=auth(unit.work_unit_id, "gpt-5.6-terra"),
            )

    def test_execution_model_cannot_override_luna_default(self):
        unit = WorkUnit("WU-NO-OVERRIDE", dimensions(task_complexity=1))
        self.assertEqual(
            self.router.route(unit).to_dict(),
            self.router.route(unit, execution_model="gpt-5.6-sol").to_dict(),
        )

    def test_missing_default_model_is_blocked_not_substituted(self):
        registry = ModelRegistry((
            ModelQualification(
                "gpt-5.6-terra",
                CapabilityClass.PRECISION,
                "openai",
                "qual-terra",
                2,
                1,
            ),
        ))
        router = DeterministicModelRouter(registry)
        with self.assertRaises(RoutingBlocked):
            router.route(WorkUnit("WU-NO-LUNA", dimensions()))

    def test_unqualified_default_model_is_blocked(self):
        registry = ModelRegistry((
            ModelQualification(
                "gpt-5.6-luna",
                CapabilityClass.MECHANICAL,
                "openai",
                "qual-luna",
                1,
                1,
                False,
            ),
        ))
        with self.assertRaises(RoutingBlocked):
            DeterministicModelRouter(registry).route(
                WorkUnit("WU-UNQUALIFIED", dimensions())
            )

    def test_escalation_requires_explicit_human_authorization(self):
        unit = WorkUnit("WU-ESCALATE", dimensions(task_complexity=1))
        previous = self.router.route(unit)
        with self.assertRaises(HumanModelAuthorizationRequired):
            self.router.escalate(
                WorkUnit("WU-ESCALATE", dimensions(architectural_impact=3)),
                previous,
            )

    def test_authorized_escalation_preserves_original_decision(self):
        unit = WorkUnit("WU-ESCALATE-OK", dimensions(task_complexity=1))
        previous = self.router.route(unit)
        escalated_unit = WorkUnit(
            "WU-ESCALATE-OK",
            dimensions(architectural_impact=3),
        )
        escalated = self.router.escalate(
            escalated_unit,
            previous,
            authorization=auth(escalated_unit.work_unit_id, "gpt-5.6-sol"),
        )
        self.assertEqual("gpt-5.6-luna", previous.selected_model)
        self.assertEqual("gpt-5.6-sol", escalated.selected_model)
        self.assertTrue(escalated.escalation_required)
        self.assertEqual(previous.decision_id, escalated.supersedes_decision_id)
        self.assertNotEqual(previous.decision_id, escalated.decision_id)

    def test_escalation_to_same_or_lower_class_is_blocked(self):
        unit = WorkUnit("WU-ESCALATE-LOW", dimensions(task_complexity=1))
        previous = self.router.route(unit)
        with self.assertRaises(RoutingBlocked):
            self.router.escalate(
                WorkUnit("WU-ESCALATE-LOW", dimensions(task_complexity=1)),
                previous,
                authorization=auth(unit.work_unit_id, "gpt-5.6-luna"),
            )

    def test_routing_decision_projects_into_run_state_schema(self):
        unit = WorkUnit("WU-STATE", dimensions(reasoning_depth=2))
        decision = self.router.route(
            unit,
            authorization=auth(unit.work_unit_id, "gpt-5.6-terra"),
        )
        state = json.loads(
            (ROOT / "tests" / "fixtures" / "valid_new_run.json").read_text(
                encoding="utf-8"
            )
        )
        state["work_units"][0]["model"] = decision.to_run_state_model()
        schema = json.loads(
            (ROOT / "schemas" / "gacm-run-state.schema.json").read_text(
                encoding="utf-8"
            )
        )
        errors = list(
            Draft202012Validator(
                schema,
                format_checker=FormatChecker(),
            ).iter_errors(state)
        )
        self.assertEqual([], errors)

    def test_routing_decision_cannot_create_authoritative_pass(self):
        decision = self.router.route(WorkUnit("WU-NO-PASS", dimensions()))
        projected = decision.to_run_state_model()
        self.assertNotIn("verification", projected)
        self.assertNotIn("authoritative_pass", projected)
        self.assertNotEqual("PASS", projected.get("status"))

    def test_identical_inputs_and_authority_are_deterministic(self):
        unit = WorkUnit("WU-DETERMINISTIC", dimensions(reasoning_depth=2))
        authorization = auth(unit.work_unit_id, "gpt-5.6-terra")
        first = self.router.route(unit, authorization=authorization).to_dict()
        second = self.router.route(unit, authorization=authorization).to_dict()
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
