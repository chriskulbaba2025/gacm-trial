"""Bind graph-derived machine work packages to durable GCU execution contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from gacm.execution.models import WorkUnitContract
from gacm.routing.models import RoutingDecision


class GraphBindingError(ValueError):
    """A graph work package cannot be safely bound to execution."""


@dataclass(frozen=True)
class BoundGraphWorkUnit:
    contract: WorkUnitContract
    graph_binding: Mapping[str, Any]

    def run_state_projection(self) -> dict[str, Any]:
        return {
            "unit_id": self.contract.work_unit_id,
            "graph_binding": dict(self.graph_binding),
        }

    def current_state_binding(self) -> dict[str, Any]:
        return {
            "graph_action_id": self.contract.graph_action_id,
            "graph_revision": self.contract.graph_revision,
            "graph_target_object_id": self.contract.graph_target_object_id,
            "graph_project_id": self.contract.graph_project_id,
        }


class GraphWorkPackageBinder:
    """Convert a scheduler package into a graph-bound WorkUnitContract."""

    def bind(
        self,
        work_package: Mapping[str, Any],
        *,
        routing_decision: RoutingDecision,
        repository_id: str,
        authorized_start_sha: str,
        branch: str,
        worktree: str,
        context_snapshot_id: str,
        context_snapshot_revision: str,
        expected_outcome: str,
        evidence_requirements: tuple[str, ...],
        broader_requalification_triggers: tuple[str, ...],
        rollback_authority: str,
        dependencies: tuple[str, ...] = (),
    ) -> BoundGraphWorkUnit:
        if work_package.get("status") != "READY_FOR_EXECUTION_GATE":
            raise GraphBindingError("graph work package is not ready for the execution gate")
        self._require_package_identity(work_package)

        if work_package.get("subagents_authorized") is True:
            raise GraphBindingError("current GACM policy does not authorize subagents")
        if work_package.get("model_escalation_authorized") is True and not routing_decision.human_authorization_id:
            raise GraphBindingError("model escalation flag lacks explicit human model authorization")

        selected_model = work_package.get("selected_model")
        qualification_identity = work_package.get("qualification_identity")
        routing_decision_id = work_package.get("routing_decision_id")
        if selected_model != routing_decision.selected_model:
            raise GraphBindingError("work package model differs from routing decision")
        if qualification_identity != routing_decision.qualification_identity:
            raise GraphBindingError("work package qualification differs from routing decision")
        if routing_decision_id != routing_decision.decision_id:
            raise GraphBindingError("work package routing decision identity differs from routing decision")
        if selected_model != "gpt-5.6-luna":
            if not routing_decision.human_authorization_id or not routing_decision.model_authority_ref:
                raise GraphBindingError("non-Luna route lacks explicit durable human authorization")

        external_action_required = work_package.get("external_action_required")
        if not isinstance(external_action_required, bool):
            raise GraphBindingError("external action classification must be explicit")

        allowed = tuple(str(item) for item in work_package.get("allowed_surfaces", ()))
        forbidden = tuple(str(item) for item in work_package.get("forbidden_surfaces", ()))
        tests = tuple(str(item) for item in work_package.get("test_contract", ()))
        stops = tuple(str(item) for item in work_package.get("stop_conditions", ()))
        if not allowed or not tests or not stops:
            raise GraphBindingError("graph work package lacks writable scope, tests, or STOP conditions")

        graph_binding = {
            "graph_action_id": str(work_package["graph_action_id"]),
            "graph_revision": int(work_package["graph_revision"]),
            "target_object_id": str(work_package["target_object_id"]),
            "project_id": str(work_package["project_id"]),
        }
        contract = WorkUnitContract(
            run_id=str(work_package["run_id"]),
            work_unit_id=str(work_package["work_unit_id"]),
            task_objective=str(work_package["task_objective"]),
            expected_outcome=expected_outcome,
            repository_id=repository_id,
            authorized_start_sha=authorized_start_sha,
            branch=branch,
            worktree=worktree,
            context_snapshot_id=context_snapshot_id,
            context_snapshot_revision=context_snapshot_revision,
            selected_model=routing_decision.selected_model,
            qualification_identity=routing_decision.qualification_identity,
            graph_action_id=graph_binding["graph_action_id"],
            graph_revision=graph_binding["graph_revision"],
            graph_target_object_id=graph_binding["target_object_id"],
            graph_project_id=graph_binding["project_id"],
            external_action_required=external_action_required,
            allowed_writable_paths=allowed,
            forbidden_paths=forbidden,
            test_contract=tests,
            evidence_requirements=evidence_requirements,
            stop_conditions=stops,
            broader_requalification_triggers=broader_requalification_triggers,
            dependencies=dependencies,
            routing_decision_id=routing_decision.decision_id,
            rollback_authority=rollback_authority,
        )
        return BoundGraphWorkUnit(contract=contract, graph_binding=graph_binding)

    @staticmethod
    def _require_package_identity(work_package: Mapping[str, Any]) -> None:
        required = (
            "work_unit_id",
            "graph_action_id",
            "graph_revision",
            "project_id",
            "run_id",
            "target_object_id",
            "task_objective",
            "selected_model",
            "qualification_identity",
            "routing_decision_id",
        )
        missing = [
            key for key in required
            if key not in work_package
            or work_package.get(key) is None
            or (isinstance(work_package.get(key), str) and not work_package.get(key).strip())
        ]
        if missing:
            raise GraphBindingError("graph work package is missing: " + ", ".join(sorted(missing)))
        revision = work_package.get("graph_revision")
        if not isinstance(revision, int) or isinstance(revision, bool) or revision < 0:
            raise GraphBindingError("graph revision must be a non-negative integer")
