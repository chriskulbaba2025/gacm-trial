"""Deterministic GACM model router."""

from __future__ import annotations

import hashlib
from collections.abc import Callable

from .models import CapabilityClass, ModelQualification, RoutingBlocked, RoutingDecision, WorkUnit
from .registry import ModelRegistry
from .risk import RiskAssessment, assess


class DeterministicModelRouter:
    """Select the least capable qualified model satisfying the risk envelope."""

    def __init__(self, registry: ModelRegistry, clock: Callable[[], str] | None = None):
        self.registry = registry
        self.clock = clock or RoutingDecision.timestamp_now

    def route(self, work_unit: WorkUnit, execution_model: str | None = None) -> RoutingDecision:
        """Create a fresh decision; execution_model is deliberately non-authoritative."""

        assessment = assess(work_unit)
        selected = self._select(assessment)
        return self._decision(work_unit, assessment, selected, False, None, None)

    def escalate(self, work_unit: WorkUnit, previous: RoutingDecision) -> RoutingDecision:
        """Create a new receipt after a prior envelope is insufficient."""

        if previous.work_unit_id != work_unit.work_unit_id:
            raise ValueError("escalation work unit does not match prior decision")
        assessment = assess(work_unit)
        previous_entry = self.registry.get(previous.selected_model)
        candidates = tuple(
            entry for entry in self.registry.qualified_for(assessment.required_class, assessment.highest_score)
            if entry.model_class > previous_entry.model_class
        )
        selected = self._select_from(candidates, assessment)
        reason = f"{previous.selected_model} envelope exceeded by {assessment.highest_risk_dimension}={assessment.highest_score}"
        return self._decision(work_unit, assessment, selected, True, previous.decision_id, reason)

    def _select(self, assessment: RiskAssessment) -> ModelQualification:
        return self._select_from(self.registry.qualified_for(assessment.required_class, assessment.highest_score), assessment)

    @staticmethod
    def _select_from(candidates: tuple[ModelQualification, ...], assessment: RiskAssessment) -> ModelQualification:
        if not candidates:
            raise RoutingBlocked(
                f"BLOCKED: no qualified model satisfies {assessment.required_class.name.lower()} capability "
                f"and risk score {assessment.highest_score}"
            )
        minimum_class = min(entry.model_class for entry in candidates)
        equivalent = tuple(entry for entry in candidates if entry.model_class == minimum_class)
        return min(equivalent, key=lambda entry: (entry.cost_rank, entry.model_id))

    def _decision(
        self,
        work_unit: WorkUnit,
        assessment: RiskAssessment,
        selected: ModelQualification,
        escalation_required: bool,
        supersedes: str | None,
        escalation_reason: str | None,
    ) -> RoutingDecision:
        stable_material = f"{work_unit.work_unit_id}|{selected.model_id}|{selected.qualification_identity}|{assessment.required_class.name}"
        decision_id = "route-" + hashlib.sha256(stable_material.encode("utf-8")).hexdigest()[:24]
        reason = (
            f"minimum qualified {selected.model_class.name.lower()} model for "
            f"{assessment.highest_risk_dimension}={assessment.highest_score}"
        )
        return RoutingDecision(
            work_unit_id=work_unit.work_unit_id,
            selected_model=selected.model_id,
            selected_model_class=selected.model_class.name.lower(),
            qualification_identity=selected.qualification_identity,
            routing_dimensions=assessment.dimensions,
            highest_risk_dimension=assessment.highest_risk_dimension,
            routing_reason=reason,
            escalation_required=escalation_required,
            decision_timestamp=self.clock(),
            provider=selected.provider,
            decision_id=decision_id if supersedes is None else decision_id + "-escalated",
            supersedes_decision_id=supersedes,
            escalation_reason=escalation_reason,
        )
