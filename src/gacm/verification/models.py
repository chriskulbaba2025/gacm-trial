"""Machine-readable independent-verification contracts."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping


class VerificationStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    UNOBSERVABLE = "UNOBSERVABLE"


SCOPE_CLASSIFICATIONS = (
    "LOCAL",
    "DEPENDENCY_EXPANDED",
    "AUTHORITY_BEARING",
    "MODEL_BEARING",
    "ARCHITECTURE_BEARING",
    "UNKNOWN",
)


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)


@dataclass(frozen=True)
class VerificationInput:
    """All observations required for one independent verification decision.

    `actual_changed_paths` is deliberately distinct from executor receipt data.
    It represents an independently obtained Git/diff observation and may be
    `None` when that observation is unavailable.
    """

    run_state: Mapping[str, Any]
    work_unit_contract: Mapping[str, Any]
    execution_receipt: Mapping[str, Any]
    starting_repository: Mapping[str, Any]
    ending_repository: Mapping[str, Any]
    actual_changed_paths: tuple[str, ...] | None
    diff_evidence: Mapping[str, Any] | None
    test_contract: tuple[str, ...]
    test_outcomes: Mapping[str, str] | None
    allowed_writable_surfaces: tuple[str, ...]
    forbidden_surfaces: tuple[str, ...]
    operational_context: Mapping[str, Any]
    routing_decision: Mapping[str, Any]
    broader_requalification_triggers: tuple[str, ...]
    claimed_affected_scope: tuple[str, ...]
    prior_assurance: tuple[Mapping[str, Any], ...] = ()
    scope_patterns: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    dependency_paths: tuple[str, ...] = ()
    expected_outcome_met: bool | None = True


@dataclass(frozen=True)
class ScopeDetermination:
    classification: str
    changed_paths: tuple[str, ...]
    affected_scope: tuple[str, ...]
    broader_requalification_required: bool
    requalification_reasons: tuple[str, ...]
    prior_assurance_invalidated: tuple[str, ...]
    prior_assurance_preserved: tuple[str, ...]
    rerun_scope: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "classification": self.classification,
            "changed_paths": list(self.changed_paths),
            "affected_scope": list(self.affected_scope),
            "broader_requalification_required": self.broader_requalification_required,
            "requalification_reasons": list(self.requalification_reasons),
            "prior_assurance_invalidated": list(self.prior_assurance_invalidated),
            "prior_assurance_preserved": list(self.prior_assurance_preserved),
            "rerun_scope": list(self.rerun_scope),
        }


@dataclass(frozen=True)
class VerificationReceipt:
    run_id: str
    work_unit_id: str
    verification_id: str
    verifier_identity: str
    status: str
    evidence_reviewed: tuple[str, ...]
    scope_checked: tuple[str, ...]
    expected_outcome_result: str
    writable_surface_result: str
    forbidden_surface_result: str
    regression_result: str
    authority_integrity_result: str
    operational_context_result: str
    model_routing_integrity_result: str
    affected_scope_determination: Mapping[str, Any]
    prior_assurance_invalidated: tuple[str, ...]
    prior_assurance_preserved: tuple[str, ...]
    broader_requalification_required: bool
    reasons: tuple[str, ...]
    started_at: str
    completed_at: str
    authoritative: bool
    issuer_role: str

    def __post_init__(self) -> None:
        if self.status not in {item.value for item in VerificationStatus}:
            raise ValueError(f"unsupported verification status: {self.status}")
        if self.authoritative != (self.issuer_role == "INDEPENDENT_VERIFIER" and self.status == "PASS"):
            raise ValueError("only an independent verifier PASS may be authoritative")

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "work_unit_id": self.work_unit_id,
            "verification_id": self.verification_id,
            "verifier_identity": self.verifier_identity,
            "status": self.status,
            "authoritative": self.authoritative,
            "issuer_role": self.issuer_role,
            "evidence_reviewed": list(self.evidence_reviewed),
            "scope_checked": list(self.scope_checked),
            "expected_outcome_result": self.expected_outcome_result,
            "writable_surface_result": self.writable_surface_result,
            "forbidden_surface_result": self.forbidden_surface_result,
            "regression_result": self.regression_result,
            "authority_integrity_result": self.authority_integrity_result,
            "operational_context_result": self.operational_context_result,
            "model_routing_integrity_result": self.model_routing_integrity_result,
            "affected_scope_determination": dict(self.affected_scope_determination),
            "prior_assurance_invalidated": list(self.prior_assurance_invalidated),
            "prior_assurance_preserved": list(self.prior_assurance_preserved),
            "broader_requalification_required": self.broader_requalification_required,
            "reasons": list(self.reasons),
            "timestamps": {"started_at": self.started_at, "completed_at": self.completed_at},
        }

    def content_sha(self) -> str:
        return hashlib.sha256(canonical(self.to_dict()).encode("utf-8")).hexdigest()[:40]

    def to_run_state_projection(self) -> dict[str, Any]:
        evidence_id = "verify-" + self.verification_id
        work_status = "PASS" if self.status == "PASS" else {
            "FAIL": "FAIL",
            "BLOCKED": "BLOCKED",
            "UNOBSERVABLE": "BLOCKED",
        }[self.status]
        return {
            "evidence": {
                "evidence_id": evidence_id,
                "kind": "INDEPENDENT_VERIFICATION_RECEIPT",
                "content_sha": self.content_sha(),
                "produced_by": "INDEPENDENT_VERIFIER",
                "recorded_at": self.completed_at,
            },
            "work_unit": {
                "status": work_status,
                "verification": {
                    "status": self.status,
                    "authoritative": self.authoritative,
                    "issuer_role": self.issuer_role,
                    "evidence_ids": [evidence_id],
                    "decision_at": self.completed_at,
                },
                "affected_scope": list(self.affected_scope_determination.get("affected_scope", [])),
                "broader_requalification_triggers": list(self.affected_scope_determination.get("requalification_reasons", [])),
                "output_evidence": [evidence_id],
            },
        }
