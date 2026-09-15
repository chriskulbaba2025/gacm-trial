"""Immutable promotion and rollback governance contracts."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping


class PromotionState(StrEnum):
    NOT_ELIGIBLE = "NOT_ELIGIBLE"
    ELIGIBLE = "ELIGIBLE"
    PROMOTION_PENDING = "PROMOTION_PENDING"
    PROMOTED = "PROMOTED"
    SETTLE_REQUIRED = "SETTLE_REQUIRED"
    OBSERVING = "OBSERVING"
    SETTLE_PASS = "SETTLE_PASS"
    SETTLE_FAIL = "SETTLE_FAIL"
    ROLLBACK_REQUIRED = "ROLLBACK_REQUIRED"
    STABLE = "STABLE"
    ROLLBACK_PENDING = "ROLLBACK_PENDING"
    ROLLED_BACK = "ROLLED_BACK"
    BLOCKED = "BLOCKED"


class PromotionTransitionError(RuntimeError):
    pass


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)


@dataclass(frozen=True)
class EligibilityResult:
    state: str
    reasons: tuple[str, ...] = ()

    @property
    def eligible(self) -> bool:
        return self.state == PromotionState.ELIGIBLE.value


@dataclass(frozen=True)
class PromotionReceipt:
    run_id: str
    promotion_id: str
    state: str
    candidate_sha: str | None
    candidate_artifact_identity: str | None
    prior_authoritative_sha: str | None
    rollback_target_sha: str | None
    verification_receipt_ids: tuple[str, ...]
    required_approvals: tuple[str, ...]
    operational_context_id: str | None
    timestamp: str
    reason: str
    settle_required: bool = False
    event_type: str = "PROMOTION"

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id, "promotion_id": self.promotion_id, "state": self.state,
            "candidate_sha": self.candidate_sha, "candidate_artifact_identity": self.candidate_artifact_identity,
            "prior_authoritative_sha": self.prior_authoritative_sha, "rollback_target_sha": self.rollback_target_sha,
            "verification_receipt_ids": list(self.verification_receipt_ids), "required_approvals": list(self.required_approvals),
            "operational_context_id": self.operational_context_id, "timestamp": self.timestamp,
            "reason": self.reason, "settle_required": self.settle_required, "event_type": self.event_type,
        }

    def content_sha(self) -> str:
        return hashlib.sha256(canonical(self.to_dict()).encode()).hexdigest()[:40]

    def to_run_state_projection(self) -> dict[str, Any]:
        return {
            "evidence": {"evidence_id": "promotion-" + self.promotion_id, "kind": "PROMOTION_RECEIPT", "content_sha": self.content_sha(), "produced_by": "ORCHESTRATION", "recorded_at": self.timestamp},
            "promotion": {"state": "PROMOTED" if self.state in {"PROMOTED", "SETTLE_REQUIRED"} else "PENDING_HUMAN", "candidate_sha": self.candidate_sha, "receipt_id": self.promotion_id},
            "promotion_history": [self.to_dict()],
        }


@dataclass(frozen=True)
class RollbackReceipt:
    run_id: str
    rollback_id: str
    state: str
    prior_authoritative_sha: str | None
    target_sha: str | None
    reason: str
    preserved_promotion_ids: tuple[str, ...]
    preserved_verification_receipt_ids: tuple[str, ...]
    timestamp: str
    event_type: str = "ROLLBACK"

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id, "rollback_id": self.rollback_id, "state": self.state,
            "prior_authoritative_sha": self.prior_authoritative_sha, "target_sha": self.target_sha,
            "reason": self.reason, "preserved_promotion_ids": list(self.preserved_promotion_ids),
            "preserved_verification_receipt_ids": list(self.preserved_verification_receipt_ids),
            "timestamp": self.timestamp, "event_type": self.event_type,
        }

    def content_sha(self) -> str:
        return hashlib.sha256(canonical(self.to_dict()).encode()).hexdigest()[:40]

    def to_run_state_projection(self) -> dict[str, Any]:
        return {
            "evidence": {"evidence_id": "rollback-" + self.rollback_id, "kind": "ROLLBACK_RECEIPT", "content_sha": self.content_sha(), "produced_by": "ORCHESTRATION", "recorded_at": self.timestamp},
            "rollback_target": {"target_sha": self.target_sha, "authority_source": {"kind": "APPROVED_DURABLE_STATE", "ref": self.target_sha or "unresolved", "content_sha": self.target_sha or "0" * 40}, "reason": self.reason, "executed_at": self.timestamp} if self.target_sha else None,
            "rollback_history": [self.to_dict()],
        }


@dataclass(frozen=True)
class SettleReceipt:
    settle_run_id: str
    candidate_sha: str
    promoted_artifact_identity: str
    prior_authoritative_sha: str
    promotion_receipt_id: str
    policy_id: str
    policy_version: str
    state: str
    authoritative_sha_observed: str
    checks_executed: tuple[str, ...]
    evidence_references: tuple[str, ...]
    result: str
    failure_reason: str | None
    started_at: str
    observed_at: str
    next_governed_action: str
    rollback_target_sha: str
    event_type: str = "SETTLE"

    def to_dict(self) -> dict[str, Any]:
        return {
            "settle_run_id": self.settle_run_id, "candidate_sha": self.candidate_sha,
            "promoted_artifact_identity": self.promoted_artifact_identity,
            "prior_authoritative_sha": self.prior_authoritative_sha,
            "promotion_receipt_id": self.promotion_receipt_id,
            "policy_id": self.policy_id, "policy_version": self.policy_version,
            "state": self.state, "authoritative_sha_observed": self.authoritative_sha_observed,
            "checks_executed": list(self.checks_executed), "evidence_references": list(self.evidence_references),
            "result": self.result, "failure_reason": self.failure_reason,
            "started_at": self.started_at, "observed_at": self.observed_at,
            "next_governed_action": self.next_governed_action,
            "rollback_target_sha": self.rollback_target_sha, "event_type": self.event_type,
        }

    def content_sha(self) -> str:
        return hashlib.sha256(canonical(self.to_dict()).encode()).hexdigest()[:40]

    def to_run_state_projection(self) -> dict[str, Any]:
        return {
            "evidence": {"evidence_id": "settle-" + self.settle_run_id + "-" + self.result.lower(), "kind": "SETTLE_RECEIPT", "content_sha": self.content_sha(), "produced_by": "ORCHESTRATION", "recorded_at": self.observed_at},
            "settle": {"state": self.state, "observed_deployment_revision": self.candidate_sha, "observation_evidence_ids": list(self.evidence_references), "observed_at": self.observed_at},
            "settle_history": [self.to_dict()],
        }
