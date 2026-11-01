import unittest

from gacm.generalization import GATE_ID, GeneralizationGate
from gacm.graph import (
    EpistemicState,
    GovernedGraph,
    GraphMutation,
    GraphNode,
    GraphScheduler,
    NodeType,
    ProducerRole,
)
from gacm.harness import HarnessAdapters, HarnessConfig, MemoryRunStateStore, PilotHarness


SHA = "a" * 40
PROJECT = "synthetic"


def generalization_contract():
    return {
        "gate_id": GATE_ID,
        "mode": "GENERALIZED",
        "product_definition_of_done": "Variable valid inputs traverse the capability end-to-end.",
        "authorized_capability_scope": ["capability"],
        "connected_system_path": ["input", "processing", "output"],
        "required_full_path_boundaries": ["input", "processing", "output"],
        "minimum_fresh_scenarios": 2,
        "reference_regression_ids": ["reference-case"],
    }


def generalization_evidence(contract):
    digest = GeneralizationGate().contract_digest(contract)
    return {
        "issuer_role": "INDEPENDENT_VERIFIER",
        "authoritative": True,
        "contract_digest": digest,
        "acceptance_boundary_unchanged": True,
        "system_map_status": "PASS",
        "whole_authorized_scope_closed": True,
        "closure_definition_of_done_met": True,
        "generalized_scenarios": [
            {
                "scenario_id": "fresh-a",
                "input_identity": "a",
                "materially_different": True,
                "reference_fixture": False,
                "runtime_path_identity": "generic",
                "boundary_results": {"input": "PASS", "processing": "PASS", "output": "PASS"},
                "evidence_ids": ["fresh-a"],
            },
            {
                "scenario_id": "fresh-b",
                "input_identity": "b",
                "materially_different": True,
                "reference_fixture": False,
                "runtime_path_identity": "generic",
                "boundary_results": {"input": "PASS", "processing": "PASS", "output": "PASS"},
                "evidence_ids": ["fresh-b"],
            },
        ],
        "fixture_dependency_scan": {
            "status": "PASS",
            "scanner_id": "scan",
            "scanned_paths": ["src/product.py"],
            "findings": [],
            "evidence_ids": ["scan"],
        },
        "reference_regression": {"status": "PASS", "evidence_ids": ["reference"]},
        "full_regression": {"status": "PASS", "evidence_ids": ["full"]},
    }


def config(
    planning_authority="GRAPH_SCHEDULER",
    *,
    execution_policy=None,
    external_provider_authority=None,
):
    policy = {"planning_authority": planning_authority}
    policy.update(execution_policy or {})
    return HarnessConfig(
        project_id=PROJECT,
        prd_identity="prd-v1",
        authoritative_start_sha=SHA,
        branch_or_worktree="isolated",
        gacm_version="4.2.2",
        execution_policy=policy,
        human_authority={"promotion_required": False},
        discovery_config={},
        operational_context_requirements={},
        generalization_contract=generalization_contract(),
        external_provider_authority=external_provider_authority or {},
    )


def graph_node(object_id, object_type=NodeType.TRANCHE, status="READY", payload=None):
    return GraphNode(
        object_id=object_id,
        project_id=PROJECT,
        run_id=None,
        object_type=object_type,
        epistemic_state=EpistemicState.OBSERVED,
        status=status,
        source="test",
        source_snapshot_id="snapshot-1",
        provenance=("test:evidence",),
        producer_role=ProducerRole.ORCHESTRATION,
        verification_state="NOT_VERIFIED",
        created_at="2026-10-03T22:00:00Z",
        payload=payload or {},
    )


def add_node(graph, item, mutation_id):
    graph.apply(
        GraphMutation(
            mutation_id=mutation_id,
            project_id=PROJECT,
            expected_revision=graph.revision,
            actor_role=ProducerRole.ORCHESTRATION,
            idempotency_key=mutation_id,
            nodes=(item,),
            rationale="test graph planning",
            evidence_refs=("test:evidence",),
            timestamp="2026-10-03T22:00:00Z",
        )
    )


def executable_payload(work_unit_id="graph-u1"):
    return {
        "work_unit_id": work_unit_id,
        "task_objective": "Execute only graph-selected work.",
        "allowed_surfaces": ["src/allowed.py"],
        "forbidden_surfaces": ["production"],
        "test_contract": ["targeted"],
        "stop_conditions": ["scope change"],
        "external_action_required": False,
        "execution_recipe": {
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
                        "allowed_values": {"command": ["targeted"]},
                    },
                    "judgment_slot_id": None,
                }],
                "bounded_judgment_slots": [],
                "acceptable_prior_states": ["EXECUTION"],
                "expected_result_states": ["DONE"],
                "evidence_requirements": ["targeted test evidence"],
                "stop_conditions": ["scope change"],
            }],
        },
    }


class CrashSignal(BaseException):
    pass


class CrashAtPlannedStore(MemoryRunStateStore):
    def __init__(self):
        super().__init__()
        self.crash_once = True

    def save(self, state):
        super().save(state)
        if self.crash_once and state.get("state") == "PLANNED":
            self.crash_once = False
            raise CrashSignal("simulated process stop after durable PLANNED state")


class PilotGraphPlanningIntegrationTests(unittest.TestCase):
    def make_harness(
        self,
        graph,
        *,
        store=None,
        legacy_units=None,
        route_hook=None,
        legacy_plan_hook=None,
        route_result=None,
    ):
        calls = {"legacy_plan": 0, "route": 0, "execute": 0, "executed_ids": []}
        legacy_units = legacy_units if legacy_units is not None else [
            {"unit_id": "legacy-only", "title": "legacy-only", "status": "PENDING"}
        ]

        def legacy_plan(c, context, supplied):
            calls["legacy_plan"] += 1
            if legacy_plan_hook:
                legacy_plan_hook()
            return legacy_units

        def route(unit):
            calls["route"] += 1
            if route_hook:
                route_hook()
            if callable(route_result):
                return route_result(unit)
            if route_result is not None:
                return dict(route_result)
            return {
                "work_unit_id": unit.get("work_unit_id"),
                "selected_model": "gpt-5.6-luna",
                "qualification_identity": "qual-luna",
                "decision_id": "route-luna-1",
            }

        def execute(unit, selected_route, context):
            calls["execute"] += 1
            calls["executed_ids"].append(unit.get("work_unit_id") or unit.get("unit_id"))
            return {"execution_status": "COMPLETED", "ending_sha": SHA}

        adapters = HarnessAdapters(
            authority=lambda c: {"status": "VERIFIED", "sha": SHA},
            discovery=lambda c, a: {"status": "DISCOVERED"},
            context=lambda c, a, d: {"status": "VERIFIED", "context_id": "ctx-1"},
            plan=legacy_plan,
            route=route,
            execute=execute,
            verify=lambda unit, execution, context: {
                "status": "PASS",
                "issuer_role": "INDEPENDENT_VERIFIER",
            },
            identity_validate=lambda unit, context: {"result": "VALID"},
            promotion=lambda state, authority: {"state": "SETTLE_REQUIRED"},
            settle=lambda state, policy: {"status": "SETTLE_PASS"},
            generalization_evidence=lambda state, contract: generalization_evidence(contract),
        )
        return (
            PilotHarness(
                adapters,
                store or MemoryRunStateStore(),
                graph_scheduler=GraphScheduler(graph),
            ),
            calls,
        )

    def test_graph_scheduler_selects_executable_units_and_legacy_plan_is_shadow_only(self):
        graph = GovernedGraph()
        add_node(graph, graph_node("tranche-1", payload=executable_payload()), "m1")
        harness, calls = self.make_harness(
            graph,
            legacy_units=[
                {"unit_id": "legacy-only-a", "status": "PENDING"},
                {"unit_id": "legacy-only-b", "status": "PENDING"},
            ],
        )

        result = harness.run(config())

        self.assertEqual("COMPLETED", result["state"])
        self.assertEqual(["graph-u1"], calls["executed_ids"])
        self.assertEqual(1, calls["legacy_plan"])
        self.assertEqual(1, calls["route"])
        self.assertEqual(1, calls["execute"])
        self.assertEqual("graph-u1", result["units"][0]["work_unit_id"])
        self.assertNotIn("legacy-only-a", [unit.get("work_unit_id") for unit in result["units"]])
        graph_plan = next(item["value"] for item in result["evidence"] if item["kind"] == "graph_plan")
        self.assertEqual("GRAPH_SCHEDULER", graph_plan["planning_authority"])
        self.assertEqual(2, graph_plan["legacy_shadow_unit_count"])
        self.assertEqual(1, graph_plan["graph_revision"])

    def test_graph_hold_package_blocks_before_route_or_execute(self):
        graph = GovernedGraph()
        add_node(graph, graph_node("tranche-hold", payload={"work_unit_id": "graph-hold"}), "m1")
        harness, calls = self.make_harness(graph)

        result = harness.run(config())

        self.assertEqual("BLOCKED", result["state"])
        self.assertIn(
            "GRAPH_WORK_PACKAGE_NOT_EXECUTABLE:HOLD_MISSING_EXTERNAL_ACTION_CLASSIFICATION",
            result["blockers"],
        )
        self.assertEqual(0, calls["route"])
        self.assertEqual(0, calls["execute"])

    def test_graph_mode_requires_scheduler(self):
        calls = {"legacy_plan": 0, "execute": 0}

        def legacy_plan(c, context, units):
            calls["legacy_plan"] += 1
            return [{"unit_id": "legacy-only"}]

        adapters = HarnessAdapters(
            authority=lambda c: {"status": "VERIFIED"},
            discovery=lambda c, a: {},
            context=lambda c, a, d: {"status": "VERIFIED"},
            plan=legacy_plan,
            route=lambda unit: {"selected_model": "Luna", "qualification_identity": "qual"},
            execute=lambda unit, route, context: calls.__setitem__("execute", calls["execute"] + 1),
            verify=lambda unit, execution, context: {"status": "PASS", "issuer_role": "INDEPENDENT_VERIFIER"},
        )
        result = PilotHarness(adapters, MemoryRunStateStore()).run(config())

        self.assertEqual("BLOCKED", result["state"])
        self.assertIn("GRAPH_SCHEDULER_REQUIRED", result["blockers"])
        self.assertEqual(0, calls["legacy_plan"])
        self.assertEqual(0, calls["execute"])

    def test_legacy_shadow_cannot_mutate_graph_eligibility(self):
        graph = GovernedGraph()
        add_node(graph, graph_node("tranche-1", payload=executable_payload()), "m1")
        mutated = {"done": False}

        def mutate_from_legacy_shadow():
            if mutated["done"]:
                return
            mutated["done"] = True
            add_node(
                graph,
                graph_node(
                    "legacy-shadow-evidence",
                    object_type=NodeType.EVIDENCE,
                    status="RECORDED",
                    payload={"note": "legacy shadow must not influence graph planning"},
                ),
                "m2",
            )

        harness, calls = self.make_harness(
            graph,
            legacy_plan_hook=mutate_from_legacy_shadow,
        )

        result = harness.run(config())

        self.assertEqual("BLOCKED", result["state"])
        self.assertIn("LEGACY_SHADOW_MUTATED_GRAPH", result["blockers"])
        self.assertEqual(1, calls["legacy_plan"])
        self.assertEqual(0, calls["route"])
        self.assertEqual(0, calls["execute"])

    def test_graph_route_receipt_must_name_exact_work_unit(self):
        graph = GovernedGraph()
        add_node(graph, graph_node("tranche-1", payload=executable_payload()), "m1")
        harness, calls = self.make_harness(
            graph,
            route_result={
                "selected_model": "gpt-5.6-luna",
                "qualification_identity": "qual-luna",
                "decision_id": "route-luna-1",
            },
        )

        result = harness.run(config())

        self.assertEqual("BLOCKED", result["state"])
        self.assertIn("GRAPH_ROUTE_WORK_UNIT_ID_MISSING", result["blockers"])
        self.assertEqual(1, calls["route"])
        self.assertEqual(0, calls["execute"])

    def test_prebound_graph_route_cannot_be_silently_replaced(self):
        graph = GovernedGraph()
        payload = executable_payload()
        payload.update({
            "selected_model": "gpt-5.6-luna",
            "qualification_identity": "qual-bound",
            "routing_decision_id": "route-bound",
        })
        add_node(graph, graph_node("tranche-bound", payload=payload), "m1")
        harness, calls = self.make_harness(
            graph,
            route_result={
                "work_unit_id": "graph-u1",
                "selected_model": "gpt-5.6-luna",
                "qualification_identity": "qual-bound",
                "decision_id": "route-other",
            },
        )

        result = harness.run(config())

        self.assertEqual("BLOCKED", result["state"])
        self.assertIn("GRAPH_BOUND_ROUTING_DECISION_MISMATCH", result["blockers"])
        self.assertEqual(1, calls["route"])
        self.assertEqual(0, calls["execute"])

    def test_prebound_graph_route_executes_when_identity_matches_exactly(self):
        graph = GovernedGraph()
        payload = executable_payload()
        payload.update({
            "selected_model": "gpt-5.6-luna",
            "qualification_identity": "qual-bound",
            "routing_decision_id": "route-bound",
        })
        add_node(graph, graph_node("tranche-bound", payload=payload), "m1")
        harness, calls = self.make_harness(
            graph,
            route_result={
                "work_unit_id": "graph-u1",
                "selected_model": "gpt-5.6-luna",
                "qualification_identity": "qual-bound",
                "decision_id": "route-bound",
            },
        )

        result = harness.run(config())

        self.assertEqual("COMPLETED", result["state"])
        self.assertEqual(["graph-u1"], calls["executed_ids"])

    def test_unknown_planning_authority_fails_before_legacy_plan(self):
        graph = GovernedGraph()
        add_node(graph, graph_node("tranche-1", payload=executable_payload()), "m1")
        harness, calls = self.make_harness(graph)

        result = harness.run(config("PROMPT_DECIDES"))

        self.assertEqual("BLOCKED", result["state"])
        self.assertIn("UNKNOWN_PLANNING_AUTHORITY", result["blockers"])
        self.assertEqual(0, calls["legacy_plan"])
        self.assertEqual(0, calls["execute"])

    def test_human_approval_only_does_not_fall_back_to_legacy_plan(self):
        graph = GovernedGraph()
        add_node(
            graph,
            graph_node(
                "approval-1",
                object_type=NodeType.HUMAN_APPROVAL,
                status="REQUIRED",
                payload={"external_action_required": False},
            ),
            "m1",
        )
        harness, calls = self.make_harness(graph)

        result = harness.run(config())

        self.assertEqual("BLOCKED", result["state"])
        self.assertIn("GRAPH_HUMAN_APPROVAL_REQUIRED", result["blockers"])
        self.assertTrue(result["human_action_required"])
        self.assertEqual(1, calls["legacy_plan"])
        self.assertEqual(0, calls["route"])
        self.assertEqual(0, calls["execute"])

    def test_any_graph_human_approval_blocks_mixed_executable_plan(self):
        graph = GovernedGraph()
        add_node(graph, graph_node("tranche-1", payload=executable_payload()), "m1")
        add_node(
            graph,
            graph_node(
                "approval-1",
                object_type=NodeType.HUMAN_APPROVAL,
                status="REQUIRED",
                payload={"external_action_required": False},
            ),
            "m2",
        )
        harness, calls = self.make_harness(graph)

        result = harness.run(config())

        self.assertEqual("BLOCKED", result["state"])
        self.assertIn("GRAPH_HUMAN_APPROVAL_REQUIRED", result["blockers"])
        self.assertEqual(0, calls["route"])
        self.assertEqual(0, calls["execute"])

    def test_external_provider_request_survives_graph_projection_and_gates(self):
        graph = GovernedGraph()
        provider_request = {
            "provider_id": "provider-a",
            "account_identity": "acct-a",
            "environment": "development",
            "endpoint_identity": "https://provider.example/v1",
            "model_api_variant": "gpt-5.6-luna",
            "credential_source_id": "windows-user:PROVIDER_A_KEY",
        }
        payload = executable_payload()
        payload.update({
            "external_action_required": True,
            "external_provider_request": provider_request,
        })
        add_node(graph, graph_node("tranche-external", payload=payload), "m1")
        harness, calls = self.make_harness(
            graph,
            route_result={
                "work_unit_id": "graph-u1",
                "selected_model": "gpt-5.6-luna",
                "qualification_identity": "qual-luna",
                "decision_id": "route-external-1",
                "provider_id": "provider-a",
                "account_identity": "acct-a",
                "environment": "development",
                "endpoint_identity": "https://provider.example/v1",
                "credential_source_id": "windows-user:PROVIDER_A_KEY",
            },
        )
        authority = {
            **provider_request,
            "service_id": "provider-a-service",
            "credential_provenance": "VERIFIED",
            "governing_authority_artifact": "test://provider-authority",
            "authorization_scope": "graph-planned external action",
            "provider_authority": "AUTHORIZED",
            "model_variant_required": True,
        }

        result = harness.run(
            config(
                execution_policy={"external_provider_authority_gate": "REQUIRED"},
                external_provider_authority=authority,
            )
        )

        self.assertEqual("COMPLETED", result["state"])
        self.assertEqual(1, calls["execute"])
        self.assertEqual(provider_request, result["units"][0]["external_provider_request"])
        self.assertEqual(2, len(result["receipts"]["provider_authority"]))
        self.assertTrue(all(item["status"] == "PASS" for item in result["receipts"]["provider_authority"]))

    def test_graph_revision_change_after_route_blocks_before_execute(self):
        graph = GovernedGraph()
        add_node(graph, graph_node("tranche-1", payload=executable_payload()), "m1")
        mutated = {"done": False}

        def mutate_graph():
            if mutated["done"]:
                return
            mutated["done"] = True
            add_node(
                graph,
                graph_node(
                    "evidence-2",
                    object_type=NodeType.EVIDENCE,
                    status="RECORDED",
                    payload={"note": "revision changes after routing"},
                ),
                "m2",
            )

        harness, calls = self.make_harness(graph, route_hook=mutate_graph)

        result = harness.run(config())

        self.assertEqual("BLOCKED", result["state"])
        self.assertIn("STALE_GRAPH_PLAN_REVISION", result["blockers"])
        self.assertEqual(1, calls["route"])
        self.assertEqual(0, calls["execute"])

    def test_resume_from_durable_planned_state_rejects_stale_graph_revision(self):
        graph = GovernedGraph()
        add_node(graph, graph_node("tranche-1", payload=executable_payload()), "m1")
        store = CrashAtPlannedStore()
        harness, calls = self.make_harness(graph, store=store)

        with self.assertRaises(CrashSignal):
            harness.run(config())

        self.assertEqual(0, calls["route"])
        self.assertEqual(0, calls["execute"])
        run_id = next(iter(store.states))
        self.assertEqual("PLANNED", store.states[run_id]["state"])

        add_node(
            graph,
            graph_node(
                "evidence-2",
                object_type=NodeType.EVIDENCE,
                status="RECORDED",
                payload={"note": "new graph evidence after durable planning"},
            ),
            "m2",
        )

        resumed = harness.run(config(), run_id=run_id, resume=True)

        self.assertEqual("BLOCKED", resumed["state"])
        self.assertIn("STALE_GRAPH_PLAN_REVISION", resumed["blockers"])
        self.assertEqual(0, calls["route"])
        self.assertEqual(0, calls["execute"])


if __name__ == "__main__":
    unittest.main()
