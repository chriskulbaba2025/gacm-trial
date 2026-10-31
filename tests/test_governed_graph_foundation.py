import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gacm.graph import (  # noqa: E402
    ActionKind,
    EdgeType,
    EpistemicState,
    GovernedGraph,
    GraphEdge,
    GraphInvariantError,
    GraphMutation,
    GraphNode,
    GraphScheduler,
    MutationReplayConflict,
    NodeType,
    ProducerRole,
    StaleGraphRevision,
)


PROJECT = "gacm-test"


def execution_recipe(work_unit_id):
    return {
        "schema": "GACM_EXECUTION_RECIPE_V1",
        "recipe_id": "recipe-" + work_unit_id,
        "version": "1",
        "state": "FROZEN",
        "work_unit_id": work_unit_id,
        "mutation_policy": "GOVERNED_REFREEZE_REQUIRED",
        "steps": [{
            "step_id": "step-1", "sequence": 1,
            "allowed_actions": [{
                "action_kind": "COMMAND", "tools": ["python"],
                "target_patterns": ["work-unit"],
                "parameter_constraints": {"allowed_keys": ["command"], "required_keys": ["command"], "string_prefixes": {"command": ["python -m unittest"]}},
                "judgment_slot_id": None,
            }],
            "bounded_judgment_slots": [],
            "acceptable_prior_states": ["EXECUTION"],
            "expected_result_states": ["DONE"],
            "evidence_requirements": ["test output"],
            "stop_conditions": ["authority mismatch"],
        }],
    }


def node(
    object_id,
    object_type=NodeType.REQUIREMENT,
    state=EpistemicState.UNKNOWN,
    status="PENDING",
    *,
    role=ProducerRole.ORCHESTRATION,
    project=PROJECT,
    authority=False,
    payload=None,
):
    return GraphNode(
        object_id=object_id,
        project_id=project,
        run_id="run-graph",
        object_type=object_type,
        epistemic_state=state,
        status=status,
        source="test-source",
        created_at="2026-10-03T20:00:00Z",
        provenance=("test:evidence",),
        authority_ref="authority:test" if authority else None,
        authority_digest="a" * 64 if authority else None,
        producer_role=role,
        verification_state="VERIFIED" if state in {EpistemicState.EVIDENCED, EpistemicState.ACCEPTED} else "NOT_VERIFIED",
        payload=payload or {},
    )


def edge(
    edge_id,
    from_id,
    to_id,
    relationship=EdgeType.DEPENDS_ON,
    state=EpistemicState.OBSERVED,
    *,
    role=ProducerRole.ORCHESTRATION,
    project=PROJECT,
    authority=False,
):
    return GraphEdge(
        edge_id=edge_id,
        project_id=project,
        run_id="run-graph",
        relationship=relationship,
        from_id=from_id,
        to_id=to_id,
        epistemic_state=state,
        source="test-source",
        created_at="2026-10-03T20:00:00Z",
        provenance=("test:evidence",),
        authority_ref="authority:test" if authority else None,
        authority_digest="b" * 64 if authority else None,
        producer_role=role,
        verification_state="VERIFIED" if state in {EpistemicState.EVIDENCED, EpistemicState.ACCEPTED} else "NOT_VERIFIED",
    )


def mutation(graph, mutation_id, *, nodes=(), edges=(), role=ProducerRole.ORCHESTRATION, key=None):
    return GraphMutation(
        mutation_id=mutation_id,
        project_id=PROJECT,
        expected_revision=graph.revision,
        actor_role=role,
        idempotency_key=key or mutation_id,
        nodes=tuple(nodes),
        edges=tuple(edges),
        rationale="test",
        evidence_refs=("test:evidence",),
        timestamp="2026-10-03T20:00:00Z",
    )


class GovernedGraphTests(unittest.TestCase):
    def test_apply_records_revision_and_snapshot(self):
        graph = GovernedGraph()
        receipt = graph.apply(mutation(graph, "m1", nodes=(node("r1"),)))
        self.assertEqual(1, graph.revision)
        self.assertEqual("APPLIED", receipt.status)
        self.assertFalse(receipt.replayed)
        snapshot = graph.snapshot(project_id=PROJECT)
        self.assertEqual(1, snapshot["revision"])
        self.assertEqual(["r1"], [item["object_id"] for item in snapshot["nodes"]])
        self.assertEqual(1, len(snapshot["mutation_receipts"]))

    def test_stale_revision_fails_closed(self):
        graph = GovernedGraph()
        graph.apply(mutation(graph, "m1", nodes=(node("r1"),)))
        stale = GraphMutation(
            mutation_id="m2",
            project_id=PROJECT,
            expected_revision=0,
            actor_role=ProducerRole.ORCHESTRATION,
            idempotency_key="m2",
            nodes=(node("r2"),),
        )
        with self.assertRaises(StaleGraphRevision):
            graph.apply(stale)
        self.assertIsNone(graph.node("r2"))

    def test_exact_replay_is_idempotent_without_revision_increment(self):
        graph = GovernedGraph()
        original = mutation(graph, "m1", nodes=(node("r1"),), key="stable-key")
        first = graph.apply(original)
        replay = graph.apply(original)
        self.assertEqual(1, graph.revision)
        self.assertEqual(first.resulting_revision, replay.resulting_revision)
        self.assertTrue(replay.replayed)
        self.assertEqual(1, len(graph.mutation_receipts))

    def test_reused_idempotency_key_with_different_content_is_rejected(self):
        graph = GovernedGraph()
        first = mutation(graph, "m1", nodes=(node("r1"),), key="stable-key")
        graph.apply(first)
        conflicting = GraphMutation(
            mutation_id="m2",
            project_id=PROJECT,
            expected_revision=graph.revision,
            actor_role=ProducerRole.ORCHESTRATION,
            idempotency_key="stable-key",
            nodes=(node("r2"),),
        )
        with self.assertRaises(MutationReplayConflict):
            graph.apply(conflicting)

    def test_discovery_cannot_create_accepted_graph_truth(self):
        graph = GovernedGraph()
        discovered = node(
            "r1",
            state=EpistemicState.ACCEPTED,
            status="APPROVED",
            role=ProducerRole.DISCOVERY,
            authority=True,
        )
        with self.assertRaisesRegex(GraphInvariantError, "discovery"):
            graph.apply(mutation(graph, "m1", nodes=(discovered,), role=ProducerRole.DISCOVERY))

    def test_executor_cannot_create_evidenced_graph_truth(self):
        graph = GovernedGraph()
        asserted = node(
            "e1",
            object_type=NodeType.EVIDENCE,
            state=EpistemicState.EVIDENCED,
            status="PASS",
            role=ProducerRole.EXECUTOR,
            authority=True,
        )
        with self.assertRaisesRegex(GraphInvariantError, "executor"):
            graph.apply(mutation(graph, "m1", nodes=(asserted,), role=ProducerRole.EXECUTOR))

    def test_accepted_or_evidenced_requires_authority_reference_and_digest(self):
        graph = GovernedGraph()
        accepted = node(
            "r1",
            state=EpistemicState.ACCEPTED,
            status="APPROVED",
            role=ProducerRole.GACM_GOVERNANCE,
            authority=False,
        )
        with self.assertRaisesRegex(GraphInvariantError, "authority reference"):
            graph.apply(mutation(graph, "m1", nodes=(accepted,), role=ProducerRole.GACM_GOVERNANCE))

    def test_edge_requires_existing_same_project_endpoints(self):
        graph = GovernedGraph()
        graph.apply(mutation(graph, "m1", nodes=(node("r1"),)))
        with self.assertRaisesRegex(GraphInvariantError, "endpoint"):
            graph.apply(mutation(graph, "m2", edges=(edge("e1", "r1", "missing"),)))

        graph2 = GovernedGraph()
        graph2.apply(mutation(graph2, "m1", nodes=(node("r1"),)))
        foreign = node("r2", project="other")
        foreign_mutation = GraphMutation(
            mutation_id="foreign",
            project_id="other",
            expected_revision=graph2.revision,
            actor_role=ProducerRole.ORCHESTRATION,
            idempotency_key="foreign",
            nodes=(foreign,),
        )
        graph2.apply(foreign_mutation)
        with self.assertRaisesRegex(GraphInvariantError, "cross-project"):
            graph2.apply(mutation(graph2, "m3", edges=(edge("e1", "r1", "r2"),)))

    def test_accepted_state_cannot_regress_to_hypothesis(self):
        graph = GovernedGraph()
        accepted = node(
            "r1",
            state=EpistemicState.ACCEPTED,
            status="APPROVED",
            role=ProducerRole.GACM_GOVERNANCE,
            authority=True,
        )
        graph.apply(mutation(graph, "m1", nodes=(accepted,), role=ProducerRole.GACM_GOVERNANCE))
        downgraded = node(
            "r1",
            state=EpistemicState.HYPOTHESIS,
            status="PENDING",
            role=ProducerRole.ORCHESTRATION,
        )
        with self.assertRaisesRegex(GraphInvariantError, "illegal epistemic transition"):
            graph.apply(mutation(graph, "m2", nodes=(downgraded,)))

    def test_mutation_history_is_append_only_in_snapshot(self):
        graph = GovernedGraph()
        graph.apply(mutation(graph, "m1", nodes=(node("r1"),)))
        graph.apply(mutation(graph, "m2", nodes=(node("r2"),)))
        snapshot = graph.snapshot(project_id=PROJECT)
        self.assertEqual(["m1", "m2"], [item["mutation_id"] for item in snapshot["mutation_history"]])
        self.assertEqual(2, len(snapshot["mutation_receipts"]))

    def test_invalid_confidence_and_unbound_superseded_state_fail_closed(self):
        graph = GovernedGraph()
        bad_confidence = GraphNode(
            object_id="bad-confidence",
            project_id=PROJECT,
            run_id="run-graph",
            object_type=NodeType.REQUIREMENT,
            epistemic_state=EpistemicState.UNKNOWN,
            status="PENDING",
            source="test-source",
            created_at="2026-10-03T20:00:00Z",
            provenance=("test:evidence",),
            producer_role=ProducerRole.ORCHESTRATION,
            confidence=1.5,
        )
        with self.assertRaisesRegex(GraphInvariantError, "confidence"):
            graph.apply(mutation(graph, "bad-confidence-m", nodes=(bad_confidence,)))

        superseded = GraphNode(
            object_id="old",
            project_id=PROJECT,
            run_id="run-graph",
            object_type=NodeType.REQUIREMENT,
            epistemic_state=EpistemicState.SUPERSEDED,
            status="CLOSED",
            source="test-source",
            created_at="2026-10-03T20:00:00Z",
            provenance=("test:evidence",),
            producer_role=ProducerRole.ORCHESTRATION,
        )
        with self.assertRaisesRegex(GraphInvariantError, "superseded_by"):
            graph.apply(mutation(graph, "bad-super-m", nodes=(superseded,)))

    def test_transitive_dependents_follow_governed_edges(self):
        graph = GovernedGraph()
        graph.apply(mutation(
            graph,
            "m1",
            nodes=(node("a"), node("b"), node("c"), node("d")),
            edges=(
                edge("ab", "b", "a"),
                edge("bc", "c", "b"),
            ),
        ))
        self.assertEqual(("b", "c"), graph.transitive_dependents(("a",)))
        self.assertNotIn("d", graph.transitive_dependents(("a",)))


class GraphSchedulerTests(unittest.TestCase):
    def build_graph(self):
        graph = GovernedGraph()
        graph.apply(mutation(
            graph,
            "m1",
            nodes=(
                node("conflict", NodeType.DECISION, EpistemicState.CONFLICTED, "BLOCKED"),
                node("gap", NodeType.EVIDENCE_GAP, EpistemicState.UNKNOWN, "OPEN"),
                node("defect", NodeType.DEFECT, EpistemicState.OBSERVED, "OPEN"),
                node("gate", NodeType.GATE, EpistemicState.OBSERVED, "PENDING"),
                node("approval", NodeType.HUMAN_APPROVAL, EpistemicState.OBSERVED, "PENDING"),
                node(
                    "tranche",
                    NodeType.TRANCHE,
                    EpistemicState.OBSERVED,
                    "READY",
                    payload={
                        "task_objective": "repair graph-owned boundary",
                        "allowed_surfaces": ["src/gacm/graph/*"],
                        "test_contract": ["python -m unittest tests.test_governed_graph_foundation"],
                        "stop_conditions": ["scope violation"],
                        "external_action_required": False,
                    },
                ),
            ),
            edges=(
                edge("gate-gap", "gate", "gap", EdgeType.BLOCKED_BY),
                edge("tranche-gate", "tranche", "gate", EdgeType.DEPENDS_ON),
            ),
        ))
        return graph

    def test_scheduler_prioritizes_unresolved_graph_state(self):
        graph = self.build_graph()
        actions = GraphScheduler(graph).next_actions(PROJECT)
        kinds = [str(item.kind) for item in actions]
        self.assertEqual(ActionKind.RESOLVE_CONFLICT, kinds[0])
        self.assertIn(ActionKind.CLOSE_EVIDENCE_GAP, kinds)
        self.assertIn(ActionKind.DIAGNOSE_DEFECT, kinds)
        self.assertIn(ActionKind.HUMAN_APPROVAL, kinds)
        self.assertNotIn(ActionKind.RUN_GATE, kinds)
        self.assertNotIn(ActionKind.EXECUTE_TRANCHE, kinds)

    def test_gate_and_tranche_become_eligible_from_graph_state_not_prompt_order(self):
        graph = self.build_graph()

        resolved_gap = node(
            "gap",
            NodeType.EVIDENCE_GAP,
            EpistemicState.EVIDENCED,
            "RESOLVED",
            role=ProducerRole.INDEPENDENT_VERIFIER,
            authority=True,
        )
        graph.apply(mutation(
            graph,
            "m2",
            nodes=(resolved_gap,),
            role=ProducerRole.INDEPENDENT_VERIFIER,
        ))
        actions = GraphScheduler(graph).next_actions(PROJECT)
        self.assertIn(ActionKind.RUN_GATE, [str(item.kind) for item in actions])

        passed_gate = node(
            "gate",
            NodeType.GATE,
            EpistemicState.ACCEPTED,
            "PASS",
            role=ProducerRole.GACM_GOVERNANCE,
            authority=True,
        )
        graph.apply(mutation(
            graph,
            "m3",
            nodes=(passed_gate,),
            role=ProducerRole.GACM_GOVERNANCE,
        ))
        actions = GraphScheduler(graph).next_actions(PROJECT)
        self.assertIn(ActionKind.EXECUTE_TRANCHE, [str(item.kind) for item in actions])

    def test_work_package_does_not_invent_model_authority(self):
        graph = self.build_graph()
        resolved_gap = node(
            "gap",
            NodeType.EVIDENCE_GAP,
            EpistemicState.EVIDENCED,
            "RESOLVED",
            role=ProducerRole.INDEPENDENT_VERIFIER,
            authority=True,
        )
        passed_gate = node(
            "gate",
            NodeType.GATE,
            EpistemicState.ACCEPTED,
            "PASS",
            role=ProducerRole.GACM_GOVERNANCE,
            authority=True,
        )
        graph.apply(mutation(graph, "m2", nodes=(resolved_gap,), role=ProducerRole.INDEPENDENT_VERIFIER))
        graph.apply(mutation(graph, "m3", nodes=(passed_gate,), role=ProducerRole.GACM_GOVERNANCE))

        scheduler = GraphScheduler(graph)
        action = next(item for item in scheduler.next_actions(PROJECT) if str(item.kind) == ActionKind.EXECUTE_TRANCHE)
        package = scheduler.project_work_package(action)
        self.assertTrue(package["routing_required"])
        self.assertIsNone(package["selected_model"])
        self.assertEqual("READY_FOR_ROUTING", package["status"])
        self.assertEqual(["src/gacm/graph/*"], package["allowed_surfaces"])

    def test_explicit_model_authority_is_carried_without_scheduler_substitution(self):
        graph = GovernedGraph()
        graph.apply(mutation(
            graph,
            "m1",
            nodes=(node(
                "tranche",
                NodeType.TRANCHE,
                EpistemicState.OBSERVED,
                "READY",
                payload={
                    "work_unit_id": "unit-tranche",
                    "selected_model": "gpt-5.6-luna",
                    "qualification_identity": "qual-luna-1",
                    "routing_decision_id": "route-luna-1",
                    "external_action_required": False,
                    "execution_recipe": execution_recipe("unit-tranche"),
                    "task_objective": "bounded graph work",
                },
            ),),
        ))
        scheduler = GraphScheduler(graph)
        action = scheduler.next_actions(PROJECT)[0]
        package = scheduler.project_work_package(action)
        self.assertFalse(package["routing_required"])
        self.assertEqual("gpt-5.6-luna", package["selected_model"])
        self.assertEqual("qual-luna-1", package["qualification_identity"])
        self.assertEqual("route-luna-1", package["routing_decision_id"])
        self.assertFalse(package["subagents_authorized"])
        self.assertFalse(package["model_escalation_authorized"])
        self.assertEqual("READY_FOR_EXECUTION_GATE", package["status"])

    def test_routed_package_without_frozen_execution_recipe_is_held(self):
        graph = GovernedGraph()
        graph.apply(mutation(
            graph,
            "m1",
            nodes=(node(
                "tranche",
                NodeType.TRANCHE,
                EpistemicState.OBSERVED,
                "READY",
                payload={
                    "work_unit_id": "unit-no-recipe",
                    "selected_model": "gpt-5.6-luna",
                    "qualification_identity": "qual-luna-1",
                    "routing_decision_id": "route-luna-1",
                    "external_action_required": False,
                    "task_objective": "must not execute without frozen recipe",
                },
            ),),
        ))
        scheduler = GraphScheduler(graph)
        package = scheduler.project_work_package(scheduler.next_actions(PROJECT)[0])
        self.assertFalse(package["routing_required"])
        self.assertEqual("HOLD_MISSING_EXECUTION_RECIPE", package["status"])
        self.assertIsNone(package["execution_recipe"])

    def test_model_name_without_route_authority_remains_routing_required(self):
        graph = GovernedGraph()
        graph.apply(mutation(
            graph,
            "m1",
            nodes=(node(
                "tranche",
                NodeType.TRANCHE,
                EpistemicState.OBSERVED,
                "READY",
                payload={
                    "selected_model": "gpt-5.6-luna",
                    "external_action_required": False,
                },
            ),),
        ))
        scheduler = GraphScheduler(graph)
        package = scheduler.project_work_package(scheduler.next_actions(PROJECT)[0])
        self.assertTrue(package["routing_required"])
        self.assertEqual("READY_FOR_ROUTING", package["status"])

    def test_missing_external_action_classification_holds_work_package(self):
        graph = GovernedGraph()
        graph.apply(mutation(
            graph,
            "m1",
            nodes=(node(
                "tranche",
                NodeType.TRANCHE,
                EpistemicState.OBSERVED,
                "READY",
                payload={
                    "selected_model": "gpt-5.6-luna",
                    "qualification_identity": "qual-luna-1",
                    "routing_decision_id": "route-luna-1",
                },
            ),),
        ))
        scheduler = GraphScheduler(graph)
        package = scheduler.project_work_package(scheduler.next_actions(PROJECT)[0])
        self.assertEqual("HOLD_MISSING_EXTERNAL_ACTION_CLASSIFICATION", package["status"])

    def test_stale_graph_action_must_be_recalculated(self):
        graph = GovernedGraph()
        graph.apply(mutation(
            graph,
            "m1",
            nodes=(node("tranche", NodeType.TRANCHE, EpistemicState.OBSERVED, "READY"),),
        ))
        scheduler = GraphScheduler(graph)
        action = scheduler.next_actions(PROJECT)[0]
        graph.apply(mutation(graph, "m2", nodes=(node("other"),)))
        with self.assertRaisesRegex(ValueError, "stale"):
            scheduler.project_work_package(action)


if __name__ == "__main__":
    unittest.main()
