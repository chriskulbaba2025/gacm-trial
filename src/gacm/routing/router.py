"""Deterministic, authority-bounded GACM model router."""

from __future__ import annotations

import hashlib
from collections.abc import Callable

from .models import (
    HumanModelAuthorizationRequired,
    ModelAuthorization,
    ModelQualification,
    RoutingBlocked,
    RoutingDecision,
    WorkUnit,
)
from .registry import ModelRegistry
from .risk import RiskAssessment, assess


class DeterministicModelRouter:
    """Use the governed default model unless a named human override authorizes another."""

    def __init__(
        self,
        registry: ModelRegistry,
        clock: Callable[[], str] | None = None,
        *,
        default_model_id: str = "gpt-5.6-luna",
    ):
        self.registry = registry
        self.clock = clock or RoutingDecision.timestamp_now
        self.default_model_id = default_model_id

    def route(
        self,
        work_unit: WorkUnit,
        execution_model: str | None = None,
        *,
        authorization: ModelAuthorization | None = None,
    ) -> RoutingDecision:
        """Create a route. execution_model remains deliberately non-authoritative."""

        assessment = assess(work_unit)
        if authorization is not None:
            selected = self._authorized_selection(work_unit, assessment, authorization)
            return self._decision(
                work_unit,
                assessment,
                selected,
                False,
                None,
                None,
                authorization,
            )

        default = self._default_model()
        if self._satisfies(default, assessment):
            return self._decision(
                work_unit,
                assessment,
                default,
                False,
                None,
                None,
                None,
            )

        raise HumanModelAuthorizationRequired(
            "HUMAN_MODEL_AUTHORIZATION_REQUIRED: "
            f"{self.default_model_id} does not satisfy "
            f"{assessment.required_class.name.lower()} capability and "
            f"{assessment.highest_risk_dimension}={assessment.highest_score}; "
            "GACM will not auto-select another model"
        )

    def escalate(
        self,
        work_unit: WorkUnit,
        previous: RoutingDecision,
        *,
        authorization: ModelAuthorization | None = None,
    ) -> RoutingDecision:
        """Create an explicitly authorized higher-capability route; never auto-escalate."""

        if previous.work_unit_id != work_unit.work_unit_id:
            raise ValueError("escalation work unit does not match prior decision")
        if authorization is None:
            raise HumanModelAuthorizationRequired(
                "HUMAN_MODEL_AUTHORIZATION_REQUIRED: model escalation requires explicit human authority"
            )
        assessment = assess(work_unit)
        selected = self._authorized_selection(work_unit, assessment, authorization)
        previous_entry = self.registry.get(previous.selected_model)
        if selected.model_class <= previous_entry.model_class:
            raise RoutingBlocked("authorized escalation model must have a higher capability class")
        reason = (
            f"human-authorized escalation from {previous.selected_model} "
            f"under {authorization.authorization_id}"
        )
        return self._decision(
            work_unit,
            assessment,
            selected,
            True,
            previous.decision_id,
            reason,
            authorization,
        )

    def _default_model(self) -> ModelQualification:
        try:
            entry = self.registry.get(self.default_model_id)
        except KeyError as error:
            raise RoutingBlocked(
                f"BLOCKED: governed default model {self.default_model_id} is not in the qualification registry"
            ) from error
        if not entry.qualified:
            raise RoutingBlocked(
                f"BLOCKED: governed default model {self.default_model_id} is not qualified"
            )
        return entry

    def _authorized_selection(
        self,
        work_unit: WorkUnit,
        assessment: RiskAssessment,
        authorization: ModelAuthorization,
    ) -> ModelQualification:
        if authorization.work_unit_id != work_unit.work_unit_id:
            raise RoutingBlocked("model authorization work unit does not match requested work")
        try:
            selected = self.registry.get(authorization.model_id)
        except KeyError as error:
            raise RoutingBlocked("authorized model is not present in the qualification registry") from error
        if not self._satisfies(selected, assessment):
            raise RoutingBlocked(
                f"authorized model {selected.model_id} does not satisfy "
                f"{assessment.required_class.name.lower()} capability and risk score {assessment.highest_score}"
            )
        return selected

    @staticmethod
    def _satisfies(entry: ModelQualification, assessment: RiskAssessment) -> bool:
        return (
            entry.qualified
            and entry.model_class >= assessment.required_class
            and entry.max_dimension_score >= assessment.highest_score
        )

    def _decision(
        self,
        work_unit: WorkUnit,
        assessment: RiskAssessment,
        selected: ModelQualification,
        escalation_required: bool,
        supersedes: str | None,
        escalation_reason: str | None,
        authorization: ModelAuthorization | None,
    ) -> RoutingDecision:
        authority_identity = (
            f"{authorization.authorization_id}|{authorization.authority_ref}"
            if authorization is not None
            else "governed-default-policy"
        )
        stable_material = (
            f"{work_unit.work_unit_id}|{selected.model_id}|"
            f"{selected.qualification_identity}|{assessment.required_class.name}|{authority_identity}"
        )
        decision_id = "route-" + hashlib.sha256(
            stable_material.encode("utf-8")
        ).hexdigest()[:24]
        if authorization is None:
            reason = (
                f"governed default model {selected.model_id}; "
                f"qualified for {assessment.highest_risk_dimension}={assessment.highest_score}"
            )
        else:
            reason = (
                f"explicit human authorization {authorization.authorization_id} selected "
                f"{selected.model_id} for {assessment.highest_risk_dimension}={assessment.highest_score}"
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
            model_authority_ref=authorization.authority_ref if authorization is not None else None,
            human_authorization_id=authorization.authorization_id if authorization is not None else None,
        )
