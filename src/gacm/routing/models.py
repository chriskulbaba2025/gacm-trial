"""Immutable contracts for deterministic GACM model routing."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import IntEnum
from typing import Any, Mapping


ROUTING_DIMENSIONS = (
    "task_complexity",
    "ambiguity",
    "blast_radius",
    "architectural_impact",
    "authority_sensitivity",
    "security_sensitivity",
    "reasoning_depth",
    "repair_complexity",
    "verification_complexity",
)


class CapabilityClass(IntEnum):
    """Ordered pilot capability classes; higher values are more capable."""

    MECHANICAL = 1
    PRECISION = 2
    ARCHITECTURE = 3


@dataclass(frozen=True)
class WorkUnit:
    """The non-model work description supplied to the router."""

    work_unit_id: str
    dimensions: Mapping[str, int]

    def __post_init__(self) -> None:
        if not self.work_unit_id.strip():
            raise ValueError("work_unit_id must not be empty")
        unknown = sorted(set(self.dimensions) - set(ROUTING_DIMENSIONS))
        if unknown:
            raise ValueError(f"unsupported routing dimensions: {', '.join(unknown)}")
        missing = sorted(set(ROUTING_DIMENSIONS) - set(self.dimensions))
        if missing:
            raise ValueError(f"missing routing dimensions: {', '.join(missing)}")
        invalid = sorted(
            key for key, value in self.dimensions.items()
            if not isinstance(value, int) or not 0 <= value <= 4
        )
        if invalid:
            raise ValueError(
                f"routing dimensions must be integer scores from 0 to 4: {', '.join(invalid)}"
            )


@dataclass(frozen=True)
class ModelQualification:
    """A durable, deterministic qualification receipt for one model."""

    model_id: str
    model_class: CapabilityClass
    provider: str
    qualification_identity: str
    max_dimension_score: int
    cost_rank: int
    qualified: bool = True

    def __post_init__(self) -> None:
        if not self.model_id.strip() or not self.provider.strip() or not self.qualification_identity.strip():
            raise ValueError("model, provider, and qualification identity are required")
        if not 0 <= self.max_dimension_score <= 4:
            raise ValueError("max_dimension_score must be between 0 and 4")
        if self.cost_rank < 0:
            raise ValueError("cost_rank must not be negative")


@dataclass(frozen=True)
class ModelAuthorization:
    """Explicit durable human authority to use a named non-default model."""

    authorization_id: str
    work_unit_id: str
    model_id: str
    authority_ref: str
    actor_id: str
    authorized_at: str

    def __post_init__(self) -> None:
        values = (
            self.authorization_id,
            self.work_unit_id,
            self.model_id,
            self.authority_ref,
            self.actor_id,
            self.authorized_at,
        )
        if any(not isinstance(value, str) or not value.strip() for value in values):
            raise ValueError("model authorization fields must all be non-empty strings")

    def to_dict(self) -> dict[str, str]:
        return {
            "authorization_id": self.authorization_id,
            "work_unit_id": self.work_unit_id,
            "model_id": self.model_id,
            "authority_ref": self.authority_ref,
            "actor_id": self.actor_id,
            "authorized_at": self.authorized_at,
        }


class RoutingBlocked(RuntimeError):
    """Raised when deterministic routing cannot produce an authorized route."""

    code = "BLOCKED"


class HumanModelAuthorizationRequired(RoutingBlocked):
    """A higher/non-default model is needed but no human authority exists."""

    code = "HUMAN_MODEL_AUTHORIZATION_REQUIRED"


@dataclass(frozen=True)
class RoutingDecision:
    """Machine-readable routing receipt; it is not a verification result."""

    work_unit_id: str
    selected_model: str
    selected_model_class: str
    qualification_identity: str
    routing_dimensions: Mapping[str, int]
    highest_risk_dimension: str
    routing_reason: str
    escalation_required: bool
    decision_timestamp: str
    provider: str
    decision_id: str
    supersedes_decision_id: str | None = None
    escalation_reason: str | None = None
    model_authority_ref: str | None = None
    human_authorization_id: str | None = None

    @classmethod
    def timestamp_now(cls) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "work_unit_id": self.work_unit_id,
            "selected_model": self.selected_model,
            "selected_model_class": self.selected_model_class,
            "qualification_identity": self.qualification_identity,
            "routing_dimensions": dict(self.routing_dimensions),
            "highest_risk_dimension": self.highest_risk_dimension,
            "routing_reason": self.routing_reason,
            "escalation_required": self.escalation_required,
            "decision_timestamp": self.decision_timestamp,
            "provider": self.provider,
            "decision_id": self.decision_id,
        }
        if self.supersedes_decision_id is not None:
            result["supersedes_decision_id"] = self.supersedes_decision_id
        if self.escalation_reason is not None:
            result["escalation_reason"] = self.escalation_reason
        if self.model_authority_ref is not None:
            result["model_authority_ref"] = self.model_authority_ref
        if self.human_authorization_id is not None:
            result["human_authorization_id"] = self.human_authorization_id
        return result

    def to_run_state_model(
        self,
        previous_decisions: tuple["RoutingDecision", ...] = (),
    ) -> dict[str, Any]:
        """Project routing evidence into the durable run-state model receipt."""

        model = {
            "model_id": self.selected_model,
            "provider": self.provider,
            "qualification_id": self.qualification_identity,
            "route_reason": self.routing_reason,
            "selected_at": self.decision_timestamp,
            "routing_decision": self.to_dict(),
        }
        if previous_decisions:
            model["routing_history"] = [
                decision.to_dict() for decision in (*previous_decisions, self)
            ]
        return model
