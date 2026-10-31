import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gacm.execution import recipe_digest  # noqa: E402
from gacm.graph import GraphBindingError, GraphWorkPackageBinder  # noqa: E402
from gacm.routing import (  # noqa: E402
    DeterministicModelRouter,
    ModelAuthorization,
    RoutingDecision,
    WorkUnit,
    default_pilot_registry,
)


SHA = "a" * 40


def execution_recipe(work_unit_id="unit-graph"):
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
                "tools": ["python"],
                "target_patterns": ["work-unit"],
                "parameter_constraints": {
                    "allowed_keys": ["command"],
                    "required_keys": ["command"],
                    "exact": {"command": "python -m unittest tests.test_jev_classification"},
                },
                "judgment_slot_id": None,
            }],
            "bounded_judgment_slots": [],
            "acceptable_prior_states": ["EXECUTION"],
            "expected_result_states": ["DONE"],
            "evidence_requirements": ["targeted test output"],
            "stop_conditions": ["authority mismatch"],
        }],
    }


def dimensions(**overrides):
    values = {name: 0 for name in (
        "task_complexity", "ambiguity", "blast_radius", "architectural_impact",
        "authority_sensitivity", "security_sensitivity", "reasoning_depth",
        "repair_complexity", "verification_complexity",
    )}
    values.update(overrides)
    return values


def luna_decision():
    router = DeterministicModelRouter(
        default_pilot_registry(),
        clock=lambda: "2026-10-03T21:15:00Z",
    )
    return router.route(WorkUnit("unit-graph", dimensions(task_complexity=1)))


def terra_decision():
    router = DeterministicModelRouter(
        default_pilot_registry(),
        clock=lambda: "2026-10-03T21:15:00Z",
    )
    unit = WorkUnit("unit-graph", dimensions(reasoning_depth=2))
    authorization = ModelAuthorization(
        authorization_id="human-terra-1",
        work_unit_id=unit.work_unit_id,
        model_id="gpt-5.6-terra",
        authority_ref="human://chris/model-authorization",
        actor_id="chris",
        authorized_at="2026-10-03T21:14:00Z",
    )
    return router.route(unit, authorization=authorization)


def package(decision, **overrides):
    values = {
        "work_unit_id": "unit-graph",
        "graph_action_id": "graph-action-abc",
        "graph_revision": 7,
        "project_id": "project-gacm",
        "run_id": "run-gacm",
        "target_object_id": "tranche-graph-2",
        "action_kind": "EXECUTE_TRANCHE",
        "task_objective": "execute the bounded graph-derived tranche",
        "allowed_surfaces": ["src/gacm/classification/*", "src/gacm/graph/*"],
        "forbidden_surfaces": ["production/*"],
        "test_contract": ["python -m unittest tests.test_jev_classification"],
        "stop_conditions": ["authority mismatch", "graph revision mismatch"],
        "execution_recipe": execution_recipe("unit-graph"),
        "authority_refs": ["github://gacm/candidate"],
        "selected_model": decision.selected_model,
        "qualification_identity": decision.qualification_identity,
        "routing_decision_id": decision.decision_id,
        "routing_required": False,
        "external_action_required": False,
        "subagents_authorized": False,
        "model_escalation_authorized": False,
        "status": "READY_FOR_EXECUTION_GATE",
    }
    values.update(overrides)
    return values


def bind(decision, **package_overrides):
    return GraphWorkPackageBinder().bind(
        package(decision, **package_overrides),
        routing_decision=decision,
        repository_id="repo-gacm",
        authorized_start_sha=SHA,
        branch="governance/gacm-graph-foundation-02-20261003",
        worktree="C:/work/gacm-graph-foundation-02",
        context_snapshot_id="ctx-graph-2",
        context_snapshot_revision="1",
        expected_outcome="bounded tranche produces governed evidence",
        evidence_requirements=("diff", "targeted-tests", "receipt"),
        broader_requalification_triggers=("ARCHITECTURE",),
        rollback_authority=SHA,
    )


class GraphExecutionBinderTests(unittest.TestCase):
    def test_luna_graph_package_binds_to_execution_contract(self):
        decision = luna_decision()
        bound = bind(decision)
        contract = bound.contract
        self.assertEqual("graph-action-abc", contract.graph_action_id)
        self.assertEqual(7, contract.graph_revision)
        self.assertEqual("tranche-graph-2", contract.graph_target_object_id)
        self.assertEqual("project-gacm", contract.graph_project_id)
        self.assertEqual(decision.decision_id, contract.routing_decision_id)
        self.assertFalse(contract.external_action_required)
        self.assertEqual(
            {
                "graph_action_id": "graph-action-abc",
                "graph_revision": 7,
                "graph_target_object_id": "tranche-graph-2",
                "graph_project_id": "project-gacm",
                "execution_authority_state": "EXECUTION",
                "execution_recipe_digest": recipe_digest(contract.execution_recipe),
            },
            bound.current_state_binding(),
        )

    def test_graph_binding_projects_into_durable_run_state_schema(self):
        decision = luna_decision()
        bound = bind(decision)
        state = json.loads(
            (ROOT / "tests" / "fixtures" / "valid_new_run.json").read_text(
                encoding="utf-8"
            )
        )
        projection = bound.run_state_projection()
        state["work_units"][0]["graph_binding"] = projection["graph_binding"]
        state["work_units"][0]["execution_authority"] = projection["execution_authority"]
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

    def test_not_ready_package_is_rejected(self):
        with self.assertRaises(GraphBindingError):
            bind(luna_decision(), status="READY_FOR_ROUTING")

    def test_routing_decision_identity_mismatch_is_rejected(self):
        with self.assertRaises(GraphBindingError):
            bind(luna_decision(), routing_decision_id="route-wrong")

    def test_subagents_are_rejected_under_current_policy(self):
        with self.assertRaises(GraphBindingError):
            bind(luna_decision(), subagents_authorized=True)

    def test_missing_external_action_classification_is_rejected(self):
        with self.assertRaises(GraphBindingError):
            bind(luna_decision(), external_action_required=None)

    def test_authorized_terra_route_can_bind(self):
        decision = terra_decision()
        bound = bind(decision)
        self.assertEqual("gpt-5.6-terra", bound.contract.selected_model)
        self.assertTrue(decision.human_authorization_id)
        self.assertTrue(decision.model_authority_ref)

    def test_non_luna_route_without_human_authority_is_rejected(self):
        base = terra_decision()
        unauthorized = RoutingDecision(
            work_unit_id=base.work_unit_id,
            selected_model=base.selected_model,
            selected_model_class=base.selected_model_class,
            qualification_identity=base.qualification_identity,
            routing_dimensions=base.routing_dimensions,
            highest_risk_dimension=base.highest_risk_dimension,
            routing_reason="invalid legacy route",
            escalation_required=False,
            decision_timestamp=base.decision_timestamp,
            provider=base.provider,
            decision_id="route-legacy-unauthorized",
        )
        with self.assertRaises(GraphBindingError):
            bind(
                unauthorized,
                routing_decision_id=unauthorized.decision_id,
                selected_model=unauthorized.selected_model,
                qualification_identity=unauthorized.qualification_identity,
            )

    def test_graph_revision_must_be_machine_integer(self):
        with self.assertRaises(GraphBindingError):
            bind(luna_decision(), graph_revision="7")


if __name__ == "__main__":
    unittest.main()
