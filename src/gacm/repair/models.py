"""Immutable contracts for deterministic repair planning."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping


class RepairClassification(StrEnum):
    LOCAL = "LOCAL"
    DEPENDENCY_EXPANDED = "DEPENDENCY_EXPANDED"
    AUTHORITY_BEARING = "AUTHORITY_BEARING"
    MODEL_BEARING = "MODEL_BEARING"
    ARCHITECTURE_BEARING = "ARCHITECTURE_BEARING"
    UNKNOWN = "UNKNOWN"


BLOCKED_FOR_SCOPE_RESOLUTION = "BLOCKED_FOR_SCOPE_RESOLUTION"


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)


@dataclass(frozen=True)
class AssuranceRecord:
    """A historical assurance receipt and its current reliance state."""

    assurance_id: str
    surfaces: tuple[str, ...] = ()
    depends_on: tuple[str, ...] = ()
    rerun_scope: tuple[str, ...] = ()
    work_unit_id: str | None = None
    historical_status: str = "PASS"
    current_reliability: str = "CURRENTLY_RELIABLE"
    receipt: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DependencyEvidence:
    """Provenance-bearing relationship evidence.

    Graphify relationships are candidates only.  ``corroborated`` must be true
    and ``source_kind`` must identify governed Git/run-state evidence before an
    edge can affect assurance.
    """

    source_kind: str
    source_ref: str
    from_unit: str
    to_unit: str
    relationship: str = "depends_on"
    corroborated: bool = False
    evidence_id: str | None = None

    @property
    def authoritative(self) -> bool:
        return self.source_kind.upper() in {"GIT", "GITHUB", "RUN_STATE", "APPROVED_DURABLE_STATE"} and self.corroborated


@dataclass(frozen=True)
class RepairPlan:
    run_id: str
    source_work_unit_id: str
    repair_plan_id: str
    classification: str
    changed_surfaces: tuple[str, ...]
    directly_affected_work_units: tuple[str, ...]
    transitively_affected_work_units: tuple[str, ...]
    assurance_preserved: tuple[str, ...]
    assurance_invalidated: tuple[str, ...]
    tests_to_rerun: tuple[str, ...]
    verifications_to_rerun: tuple[str, ...]
    authority_revalidation_required: bool
    model_requalification_required: bool
    architecture_requalification_required: bool
    full_run_replay_required: bool
    status: str
    reasons: tuple[str, ...]
    evidence: tuple[str, ...]
    timestamp: str
    historical_pass_receipts: tuple[str, ...] = ()
    currently_reliable_assurance: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "source_work_unit_id": self.source_work_unit_id,
            "repair_plan_id": self.repair_plan_id,
            "classification": self.classification,
            "changed_surfaces": list(self.changed_surfaces),
            "directly_affected_work_units": list(self.directly_affected_work_units),
            "transitively_affected_work_units": list(self.transitively_affected_work_units),
            "assurance_preserved": list(self.assurance_preserved),
            "assurance_invalidated": list(self.assurance_invalidated),
            "tests_to_rerun": list(self.tests_to_rerun),
            "verifications_to_rerun": list(self.verifications_to_rerun),
            "authority_revalidation_required": self.authority_revalidation_required,
            "model_requalification_required": self.model_requalification_required,
            "architecture_requalification_required": self.architecture_requalification_required,
            "full_run_replay_required": self.full_run_replay_required,
            "status": self.status,
            "reasons": list(self.reasons),
            "evidence": list(self.evidence),
            "timestamp": self.timestamp,
            "historical_pass_receipts": list(self.historical_pass_receipts),
            "currently_reliable_assurance": list(self.currently_reliable_assurance),
        }

    def content_sha(self) -> str:
        return hashlib.sha256(_canonical(self.to_dict()).encode()).hexdigest()[:40]

    def to_run_state_projection(self) -> dict[str, Any]:
        """Return an append-only evidence record plus non-authoritative updates."""
        return {
            "evidence": {
                "evidence_id": "repair-" + self.repair_plan_id,
                "kind": "REPAIR_SCOPE_PLAN",
                "content_sha": self.content_sha(),
                "produced_by": "ORCHESTRATION",
                "recorded_at": self.timestamp,
            },
            "repair_plan": self.to_dict(),
        }
