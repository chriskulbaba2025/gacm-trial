"""Promotion and rollback state machine; authority changes require governance."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Callable, Mapping

from .eligibility import PromotionEligibility
from .models import EligibilityResult, PromotionReceipt, PromotionState, PromotionTransitionError, RollbackReceipt, canonical


class PromotionRollbackStateMachine:
    def __init__(self, clock: Callable[[], str] | None = None, eligibility: PromotionEligibility | None = None):
        self.clock = clock or (lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
        self.eligibility = eligibility or PromotionEligibility()
        self.state = PromotionState.NOT_ELIGIBLE.value
        self.current_authority_sha: str | None = None
        self.intent: dict[str, Any] | None = None
        self.promotion_history: list[PromotionReceipt] = []
        self.rollback_history: list[RollbackReceipt] = []
        self.settle: dict[str, Any] | None = None
        self.settle_history: list[Any] = []

    def assess(self, evidence: Mapping[str, Any]) -> EligibilityResult:
        result = self.eligibility.evaluate(evidence)
        self.state = result.state
        return result

    def create_promotion_intent(self, evidence: Mapping[str, Any], *, actor_role: str = "GACM_GOVERNANCE") -> PromotionReceipt:
        self._governance_actor(actor_role)
        result = self.assess(evidence)
        if not result.eligible: raise PromotionTransitionError("candidate is not eligible: " + ", ".join(result.reasons))
        prior = evidence.get("current_authoritative_sha")
        if not prior or evidence.get("authority_continuity") is False: self.state = PromotionState.BLOCKED.value; raise PromotionTransitionError("current authoritative identity is not continuous")
        material = {"run_id": evidence.get("run_id"), "candidate_sha": evidence.get("candidate_sha"), "prior": prior, "verifications": sorted(evidence.get("verification_receipt_ids", ())), "context": evidence.get("operational_context_id")}
        promotion_id = "promotion-" + hashlib.sha256(canonical(material).encode()).hexdigest()[:24]
        receipt = PromotionReceipt(str(evidence.get("run_id", "")), promotion_id, PromotionState.PROMOTION_PENDING.value, str(evidence["candidate_sha"]), str(evidence["candidate_artifact_identity"]), str(prior), str(evidence["rollback_target_sha"]), tuple(sorted(map(str, evidence.get("verification_receipt_ids", ())))), tuple(sorted(map(str, evidence.get("required_approvals", ())))), evidence.get("operational_context_id"), self.clock(), "durable promotion intent recorded before authority mutation")
        self.intent = dict(evidence, promotion_id=promotion_id, prior_authoritative_sha=prior)
        self.state = PromotionState.PROMOTION_PENDING.value
        self.promotion_history.append(receipt)
        return receipt

    def promote(self, *, current_authoritative_sha: str, actor_role: str = "GACM_GOVERNANCE") -> PromotionReceipt:
        self._governance_actor(actor_role)
        if self.state != PromotionState.PROMOTION_PENDING or not self.intent: raise PromotionTransitionError("promotion requires PROMOTION_PENDING intent")
        if current_authoritative_sha != self.intent.get("prior_authoritative_sha"): self.state = PromotionState.BLOCKED.value; raise PromotionTransitionError("current authority changed after intent")
        self.current_authority_sha = str(self.intent["candidate_sha"])
        settle = bool(self.intent.get("settle_required", False))
        self.state = PromotionState.SETTLE_REQUIRED.value if settle else PromotionState.PROMOTED.value
        receipt = PromotionReceipt(str(self.intent.get("run_id", "")), str(self.intent["promotion_id"]), self.state, str(self.intent["candidate_sha"]), str(self.intent["candidate_artifact_identity"]), str(self.intent["prior_authoritative_sha"]), str(self.intent["rollback_target_sha"]), tuple(sorted(map(str, self.intent.get("verification_receipt_ids", ())))), tuple(sorted(map(str, self.intent.get("required_approvals", ())))), self.intent.get("operational_context_id"), self.clock(), "candidate promoted by GACM governance", settle)
        self.promotion_history.append(receipt)
        return receipt

    def request_rollback(self, *, run_id: str, current_authoritative_sha: str, rollback_target_sha: str | None, known_good_targets: Mapping[str, Any], reason: str, preserved_verification_receipt_ids: tuple[str, ...] = (), actor_role: str = "GACM_GOVERNANCE") -> RollbackReceipt:
        self._governance_actor(actor_role)
        if self.state not in {PromotionState.PROMOTED.value, PromotionState.SETTLE_REQUIRED.value, PromotionState.OBSERVING.value, PromotionState.SETTLE_FAIL.value, PromotionState.ROLLBACK_REQUIRED.value, PromotionState.PROMOTION_PENDING.value, PromotionState.BLOCKED.value}: raise PromotionTransitionError("rollback is not legal from current promotion state")
        if not rollback_target_sha or rollback_target_sha not in known_good_targets or current_authoritative_sha != self.current_authority_sha: self.state = PromotionState.BLOCKED.value; raise PromotionTransitionError("rollback target or current authority cannot be proven")
        self.state = PromotionState.ROLLBACK_PENDING.value
        rollback_id = "rollback-" + hashlib.sha256(canonical({"run_id": run_id, "current": current_authoritative_sha, "target": rollback_target_sha, "reason": reason}).encode()).hexdigest()[:24]
        receipt = RollbackReceipt(run_id, rollback_id, self.state, current_authoritative_sha, rollback_target_sha, reason, tuple(item.promotion_id for item in self.promotion_history), tuple(sorted(preserved_verification_receipt_ids)), self.clock())
        self.rollback_history.append(receipt)
        return receipt

    def stabilize(self, *, current_authoritative_sha: str, actor_role: str = "GACM_GOVERNANCE") -> None:
        self._governance_actor(actor_role)
        if self.state != PromotionState.SETTLE_PASS.value or not self.settle:
            raise PromotionTransitionError("STABLE requires SETTLE_PASS")
        if current_authoritative_sha != self.settle["candidate_sha"] or self.current_authority_sha != current_authoritative_sha:
            self.state = PromotionState.BLOCKED.value
            raise PromotionTransitionError("stable transition authority continuity mismatch")
        self.state = PromotionState.STABLE.value

    def begin_settle(self, policy: Any, *, current_authoritative_sha: str, authority_continuity: bool = True) -> str:
        from .settle import SettleObservationGate
        return SettleObservationGate(clock=self.clock).begin(self, policy, current_authoritative_sha=current_authoritative_sha, authority_continuity=authority_continuity)

    def observe_settle(self, checks: Mapping[str, Any], *, current_authoritative_sha: str, evidence_references: tuple[str, ...] = ()) -> Any:
        from .settle import SettleObservationGate
        return SettleObservationGate(clock=self.clock).observe(self, checks, current_authoritative_sha=current_authoritative_sha, evidence_references=evidence_references)

    def finalize_settle(self, *, current_authoritative_sha: str) -> Any:
        from .settle import SettleObservationGate
        return SettleObservationGate(clock=self.clock).finalize(self, current_authoritative_sha=current_authoritative_sha)

    def execute_rollback(self, *, rollback_id: str, current_authoritative_sha: str, actor_role: str = "GACM_GOVERNANCE") -> RollbackReceipt:
        self._governance_actor(actor_role)
        if self.state != PromotionState.ROLLBACK_PENDING: raise PromotionTransitionError("rollback requires ROLLBACK_PENDING")
        previous = self.rollback_history[-1]
        if previous.rollback_id != rollback_id or previous.prior_authoritative_sha != current_authoritative_sha: self.state = PromotionState.BLOCKED.value; raise PromotionTransitionError("rollback continuity mismatch")
        self.current_authority_sha = previous.target_sha
        self.state = PromotionState.ROLLED_BACK.value
        receipt = RollbackReceipt(previous.run_id, previous.rollback_id, self.state, previous.prior_authoritative_sha, previous.target_sha, previous.reason, previous.preserved_promotion_ids, previous.preserved_verification_receipt_ids, self.clock())
        self.rollback_history.append(receipt)
        return receipt

    def mark_complete(self) -> None:
        raise PromotionTransitionError("Phase 11 cannot mark a run COMPLETE; SETTLE is Phase 12")

    @staticmethod
    def _governance_actor(actor_role: str) -> None:
        if actor_role not in {"GACM_GOVERNANCE", "RELEASE_AUTHORITY", "HUMAN"}: raise PromotionTransitionError("executor and independent verifier cannot promote or roll back")
