"""Deterministic graph-derived next-action planning.

The scheduler does not call a model and does not render a prompt. It converts
governed graph state into bounded action/work-package candidates.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping

from .models import EdgeType, EpistemicState, GraphNode, NodeType
from .store import GovernedGraph


class ActionKind(StrEnum):
    RESOLVE_CONFLICT = "RESOLVE_CONFLICT"
    CLOSE_EVIDENCE_GAP = "CLOSE_EVIDENCE_GAP"
    DIAGNOSE_DEFECT = "DIAGNOSE_DEFECT"
    COLLECT_EVIDENCE = "COLLECT_EVIDENCE"
    RUN_GATE = "RUN_GATE"
    VERIFY_REQUIREMENT = "VERIFY_REQUIREMENT"
    HUMAN_APPROVAL = "HUMAN_APPROVAL"
    EXECUTE_TRANCHE = "EXECUTE_TRANCHE"


_PRIORITY = {
    ActionKind.RESOLVE_CONFLICT: 10,
    ActionKind.CLOSE_EVIDENCE_GAP: 20,
    ActionKind.DIAGNOSE_DEFECT: 30,
    ActionKind.COLLECT_EVIDENCE: 40,
    ActionKind.RUN_GATE: 50,
    ActionKind.VERIFY_REQUIREMENT: 60,
    ActionKind.HUMAN_APPROVAL: 70,
    ActionKind.EXECUTE_TRANCHE: 80,
}


@dataclass(frozen=True)
class GraphAction:
    action_id: str
    kind: ActionKind | str
    project_id: str
    graph_revision: int
    target_object_id: str
    reason: str
    blocking_object_ids: tuple[str, ...] = ()
    authority_refs: tuple[str, ...] = ()
    payload: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "kind": str(self.kind),
            "project_id": self.project_id,
            "graph_revision": self.graph_revision,
            "target_object_id": self.target_object_id,
            "reason": self.reason,
            "blocking_object_ids": list(self.blocking_object_ids),
            "authority_refs": list(self.authority_refs),
            "payload": dict(self.payload),
        }


class GraphScheduler:
    """Derive eligible work from graph state, not conversational sequencing."""

    def __init__(self, graph: GovernedGraph):
        self.graph = graph

    def next_actions(
        self,
        project_id: str,
        *,
        run_id: str | None = None,
        limit: int | None = None,
    ) -> tuple[GraphAction, ...]:
        nodes = tuple(
            node for node in self.graph.nodes
            if node.project_id == project_id
            and (run_id is None or node.run_id in {None, run_id})
            and str(node.epistemic_state) != EpistemicState.SUPERSEDED
        )
        actions: list[GraphAction] = []

        for node in nodes:
            action = self._action_for(node)
            if action is not None:
                actions.append(action)

        actions.sort(key=lambda item: (_PRIORITY[ActionKind(str(item.kind))], item.target_object_id, item.action_id))
        if limit is not None:
            actions = actions[: max(0, int(limit))]
        return tuple(actions)

    def _action_for(self, node: GraphNode) -> GraphAction | None:
        state = EpistemicState(str(node.epistemic_state))
        node_type = NodeType(str(node.object_type))
        status = node.status.upper()

        if state == EpistemicState.CONFLICTED:
            return self._build(
                ActionKind.RESOLVE_CONFLICT,
                node,
                "Conflicted graph state must be resolved before dependent work can rely on it.",
            )

        if node_type == NodeType.EVIDENCE_GAP and status not in {"CLOSED", "RESOLVED", "PASS"}:
            return self._build(
                ActionKind.CLOSE_EVIDENCE_GAP,
                node,
                "An evidence gap remains open.",
            )

        if node_type == NodeType.DEFECT and status in {"OPEN", "FAIL", "FAILED", "BLOCKED", "REPAIR_REQUIRED"}:
            root_edges = self.graph.incoming(node.object_id, (EdgeType.EXPLAINS,))
            proven = any(
                EpistemicState(str(edge.epistemic_state)) in {EpistemicState.EVIDENCED, EpistemicState.ACCEPTED}
                for edge in root_edges
            )
            if not proven:
                return self._build(
                    ActionKind.DIAGNOSE_DEFECT,
                    node,
                    "Defect has no evidenced or accepted owning root cause.",
                )

        if node_type in {NodeType.UNKNOWN, NodeType.ASSUMPTION} and state in {
            EpistemicState.UNKNOWN,
            EpistemicState.HYPOTHESIS,
            EpistemicState.INFERRED,
        }:
            return self._build(
                ActionKind.COLLECT_EVIDENCE,
                node,
                "Current graph state is not strong enough to govern a decision.",
            )

        if node_type == NodeType.GATE and status in {"PENDING", "READY", "BLOCKED", "NOT_RUN"}:
            blockers = self._unresolved_blockers(node.object_id)
            if not blockers:
                return self._build(
                    ActionKind.RUN_GATE,
                    node,
                    "Gate prerequisites are resolved and the gate is eligible to run.",
                )

        if node_type == NodeType.REQUIREMENT and status in {"PENDING", "READY", "IMPLEMENTED", "VERIFYING"}:
            test_edges = self.graph.outgoing(node.object_id, (EdgeType.VERIFIED_BY,))
            tests = tuple(self.graph.node(edge.to_id) for edge in test_edges)
            verified = bool(tests) and all(
                test is not None
                and (
                    test.status.upper() in {"PASS", "PASSED", "COMPLETE", "COMPLETED"}
                    or EpistemicState(str(test.epistemic_state)) in {EpistemicState.EVIDENCED, EpistemicState.ACCEPTED}
                )
                for test in tests
            )
            if not verified:
                blockers = self._unresolved_dependencies(node.object_id)
                if not blockers:
                    return self._build(
                        ActionKind.VERIFY_REQUIREMENT,
                        node,
                        "Requirement lacks complete governed verification.",
                    )

        if node_type == NodeType.HUMAN_APPROVAL and status in {"PENDING", "REQUIRED", "AWAITING_HUMAN"}:
            return self._build(
                ActionKind.HUMAN_APPROVAL,
                node,
                "Explicit human authority is required.",
            )

        if node_type == NodeType.TRANCHE and status in {"PENDING", "READY"}:
            blockers = tuple(sorted(set(
                self._unresolved_dependencies(node.object_id)
                + self._unresolved_blockers(node.object_id)
            )))
            if not blockers:
                return self._build(
                    ActionKind.EXECUTE_TRANCHE,
                    node,
                    "All governed tranche prerequisites are satisfied.",
                )

        return None

    def _unresolved_dependencies(self, object_id: str) -> tuple[str, ...]:
        blockers = []
        for edge in self.graph.outgoing(object_id, (EdgeType.DEPENDS_ON, EdgeType.REQUIRES)):
            target = self.graph.node(edge.to_id)
            if target is None or not self._resolved(target):
                blockers.append(edge.to_id)
        return tuple(sorted(set(blockers)))

    def _unresolved_blockers(self, object_id: str) -> tuple[str, ...]:
        blockers = []
        for edge in self.graph.outgoing(object_id, (EdgeType.BLOCKED_BY,)):
            target = self.graph.node(edge.to_id)
            if target is None or not self._resolved(target):
                blockers.append(edge.to_id)
        return tuple(sorted(set(blockers)))

    @staticmethod
    def _resolved(node: GraphNode) -> bool:
        if node.status.upper() in {"PASS", "PASSED", "COMPLETE", "COMPLETED", "RESOLVED", "CLOSED", "APPROVED"}:
            return True
        return EpistemicState(str(node.epistemic_state)) in {
            EpistemicState.EVIDENCED,
            EpistemicState.ACCEPTED,
            EpistemicState.SUPERSEDED,
        }

    def _build(self, kind: ActionKind, node: GraphNode, reason: str) -> GraphAction:
        blockers = tuple(sorted(set(
            self._unresolved_dependencies(node.object_id)
            + self._unresolved_blockers(node.object_id)
        )))
        authority_refs = tuple(sorted({
            ref
            for ref in (
                node.authority_ref,
                *(
                    edge.authority_ref
                    for edge in self.graph.incoming(node.object_id) + self.graph.outgoing(node.object_id)
                ),
            )
            if ref
        }))
        seed = {
            "kind": str(kind),
            "project_id": node.project_id,
            "revision": self.graph.revision,
            "target": node.object_id,
        }
        action_id = "graph-action-" + hashlib.sha256(
            json.dumps(seed, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()[:20]
        return GraphAction(
            action_id=action_id,
            kind=kind,
            project_id=node.project_id,
            graph_revision=self.graph.revision,
            target_object_id=node.object_id,
            reason=reason,
            blocking_object_ids=blockers,
            authority_refs=authority_refs,
            payload=dict(node.payload),
        )

    def project_work_package(self, action: GraphAction) -> dict[str, Any]:
        """Project a bounded machine package.

        This intentionally does not render an LLM prompt. Routing and execution
        adapters may consume this package after their own authority gates.
        """
        node = self.graph.node(action.target_object_id)
        if node is None:
            raise ValueError("graph action target no longer exists")
        if action.graph_revision != self.graph.revision:
            raise ValueError("graph action is stale; recalculate from current graph revision")

        payload = dict(node.payload)
        selected_model = payload.get("selected_model")
        qualification_identity = payload.get("qualification_identity")
        routing_decision_id = payload.get("routing_decision_id")
        external_action_required = payload.get("external_action_required")
        route_complete = bool(selected_model and qualification_identity and routing_decision_id)
        if not isinstance(external_action_required, bool):
            package_status = "HOLD_MISSING_EXTERNAL_ACTION_CLASSIFICATION"
        elif not route_complete:
            package_status = "READY_FOR_ROUTING"
        else:
            package_status = "READY_FOR_EXECUTION_GATE"
        return {
            "work_unit_id": payload.get("work_unit_id", action.action_id),
            "graph_action_id": action.action_id,
            "graph_revision": self.graph.revision,
            "project_id": action.project_id,
            "run_id": node.run_id,
            "target_object_id": node.object_id,
            "action_kind": str(action.kind),
            "task_objective": payload.get("task_objective", action.reason),
            "allowed_surfaces": list(payload.get("allowed_surfaces", ())),
            "forbidden_surfaces": list(payload.get("forbidden_surfaces", ())),
            "test_contract": list(payload.get("test_contract", ())),
            "stop_conditions": list(payload.get("stop_conditions", ())),
            "authority_refs": list(action.authority_refs),
            "selected_model": selected_model,
            "qualification_identity": qualification_identity,
            "routing_decision_id": routing_decision_id,
            "routing_required": not route_complete,
            "external_action_required": external_action_required,
            "subagents_authorized": bool(payload.get("subagents_authorized", False)),
            "model_escalation_authorized": bool(payload.get("model_escalation_authorized", False)),
            "status": package_status,
        }

    def plan_work_packages(
        self,
        project_id: str,
        *,
        run_id: str | None = None,
        limit: int | None = None,
    ) -> tuple[dict[str, Any], ...]:
        return tuple(
            self.project_work_package(action)
            for action in self.next_actions(project_id, run_id=run_id, limit=limit)
            if ActionKind(str(action.kind)) != ActionKind.HUMAN_APPROVAL
        )
