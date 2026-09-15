"""Deterministic post-promotion settle policy and observation gate."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Mapping

from .models import PromotionState, PromotionTransitionError, SettleReceipt, canonical


@dataclass(frozen=True)
class SettlePolicy:
    policy_id: str
    version: str
    required_checks: tuple[str, ...]
    optional_checks: tuple[str, ...] = ()
    observation_window_seconds: int = 300
    minimum_successful_observations: int = 1
    immediate_fail_conditions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        all_checks = self.required_checks + self.optional_checks
        if not self.policy_id or not self.version or not self.required_checks:
            raise ValueError("settle policy requires identity and mandatory checks")
        if len(set(all_checks)) != len(all_checks) or not all_checks or any(not c for c in all_checks):
            raise ValueError("settle policy checks must be unique and non-empty")
        if self.observation_window_seconds <= 0 or self.minimum_successful_observations <= 0:
            raise ValueError("settle policy bounds must be positive")
        if any(c not in all_checks for c in self.immediate_fail_conditions):
            raise ValueError("immediate-fail condition must name a policy check")


class SettleObservationGate:
    def __init__(self, clock: Callable[[], str] | None = None):
        self.clock = clock or (lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    def begin(self, machine: Any, policy: SettlePolicy, *, current_authoritative_sha: str, authority_continuity: bool = True) -> str:
        if machine.state != PromotionState.SETTLE_REQUIRED.value or not machine.intent:
            raise PromotionTransitionError("settle requires Phase 11 SETTLE_REQUIRED")
        intent = machine.intent
        candidate_value = intent.get("candidate_sha"); prior_value = intent.get("prior_authoritative_sha"); target_value = intent.get("rollback_target_sha")
        candidate = str(candidate_value or ""); prior = str(prior_value or ""); target = str(target_value or "")
        promotion = machine.promotion_history[-1] if machine.promotion_history else None
        if not candidate or not prior or not target or not promotion or promotion.state != PromotionState.SETTLE_REQUIRED.value:
            machine.state = PromotionState.BLOCKED.value
            raise PromotionTransitionError("settle entry identity, receipt, or rollback target is incomplete")
        if not authority_continuity or current_authoritative_sha != candidate or machine.current_authority_sha != candidate:
            machine.state = PromotionState.BLOCKED.value
            raise PromotionTransitionError("authoritative identity changed before settle")
        settle_id = "settle-" + hashlib.sha256(canonical({"promotion": promotion.promotion_id, "candidate": candidate, "policy": policy.policy_id, "version": policy.version}).encode()).hexdigest()[:24]
        machine.settle = {"settle_run_id": settle_id, "candidate_sha": candidate, "promoted_artifact_identity": str(intent.get("candidate_artifact_identity")), "prior_authoritative_sha": prior, "promotion_receipt_id": promotion.promotion_id, "policy": policy, "started_at": self.clock(), "rollback_target_sha": target, "successful_observations": 0, "observations": []}
        machine.state = PromotionState.OBSERVING.value
        return settle_id

    def observe(self, machine: Any, checks: Mapping[str, Any], *, current_authoritative_sha: str, evidence_references: tuple[str, ...] = ()) -> SettleReceipt:
        if machine.state != PromotionState.OBSERVING or not getattr(machine, "settle", None):
            raise PromotionTransitionError("observation requires OBSERVING")
        data = machine.settle; policy: SettlePolicy = data["policy"]
        observed_at = self.clock()
        names = tuple(sorted(map(str, checks)))
        observation_key = hashlib.sha256(canonical({"checks": checks, "refs": sorted(evidence_references), "authority": current_authoritative_sha}).encode()).hexdigest()
        for key, prior in data.get("observation_receipts", []):
            if key == observation_key:
                return prior
        missing = sorted(set(policy.required_checks) - set(names))
        unknown = sorted(set(names) - set(policy.required_checks) - set(policy.optional_checks))
        bad = [name for name in names if name in checks and checks[name] not in (True, "PASS", "pass")]
        immediate = sorted(set(bad) & set(policy.immediate_fail_conditions))
        if current_authoritative_sha != data["candidate_sha"]:
            return self._remember_terminal(machine, observation_key, self._terminal(machine, PromotionState.BLOCKED.value, current_authoritative_sha, names, evidence_references, "AUTHORITY_CHANGED_DURING_OBSERVATION", observed_at, "REPAIR_OR_REVALIDATE"))
        if unknown or missing or immediate:
            reason = "UNKNOWN_CHECK" if unknown else "MANDATORY_OBSERVATION_MISSING" if missing else "IMMEDIATE_FAIL_CONDITION"
            return self._remember_terminal(machine, observation_key, self._terminal(machine, PromotionState.SETTLE_FAIL.value, current_authoritative_sha, names, evidence_references, reason, observed_at, "ROLLBACK_REQUIRED"))
        if bad:
            return self._remember_terminal(machine, observation_key, self._terminal(machine, PromotionState.SETTLE_FAIL.value, current_authoritative_sha, names, evidence_references, "OBSERVATION_CHECK_FAILED", observed_at, "ROLLBACK_REQUIRED"))
        data["successful_observations"] += 1; data["observations"].append((names, evidence_references, observed_at))
        return self._remember_terminal(machine, observation_key, self._receipt(machine, PromotionState.OBSERVING.value, current_authoritative_sha, names, evidence_references, "OBSERVING", None, observed_at, "OBSERVE_AGAIN_OR_FINALIZE"))

    def finalize(self, machine: Any, *, current_authoritative_sha: str) -> SettleReceipt:
        if machine.state != PromotionState.OBSERVING or not getattr(machine, "settle", None):
            raise PromotionTransitionError("finalize requires OBSERVING")
        data = machine.settle; policy: SettlePolicy = data["policy"]
        if current_authoritative_sha != data["candidate_sha"]:
            return self._terminal(machine, PromotionState.BLOCKED.value, current_authoritative_sha, (), (), "AUTHORITY_CHANGED_DURING_OBSERVATION", self.clock(), "REPAIR_OR_REVALIDATE")
        if data["successful_observations"] < policy.minimum_successful_observations:
            return self._terminal(machine, PromotionState.SETTLE_FAIL.value, current_authoritative_sha, (), (), "MINIMUM_SUCCESSFUL_OBSERVATIONS_NOT_REACHED", self.clock(), "ROLLBACK_REQUIRED")
        return self._terminal(machine, PromotionState.SETTLE_PASS.value, current_authoritative_sha, tuple(sorted(policy.required_checks)), tuple(ref for _, refs, _ in data["observations"] for ref in refs), None, self.clock(), "STABLE")

    complete = finalize

    def _terminal(self, machine: Any, state: str, authority: str, checks: tuple[str, ...], refs: tuple[str, ...], reason: str, at: str, next_action: str) -> SettleReceipt:
        receipt = self._receipt(machine, state, authority, checks, refs, "FAIL" if state != PromotionState.SETTLE_PASS.value else "PASS", reason, at, next_action)
        if state == PromotionState.SETTLE_FAIL.value:
            machine.state = PromotionState.ROLLBACK_REQUIRED.value
        return receipt

    def _receipt(self, machine: Any, state: str, authority: str, checks: tuple[str, ...], refs: tuple[str, ...], result: str, reason: str | None, at: str, next_action: str) -> SettleReceipt:
        data = machine.settle; policy: SettlePolicy = data["policy"]
        machine.state = state
        receipt = SettleReceipt(data["settle_run_id"], data["candidate_sha"], data["promoted_artifact_identity"], data["prior_authoritative_sha"], data["promotion_receipt_id"], policy.policy_id, policy.version, state, authority, checks, tuple(sorted(refs)), result, reason, data["started_at"], at, next_action, data["rollback_target_sha"])
        machine.settle_history.append(receipt)
        return receipt

    @staticmethod
    def _remember_terminal(machine: Any, key: str, receipt: SettleReceipt) -> SettleReceipt:
        machine.settle.setdefault("observation_receipts", []).append((key, receipt))
        return receipt
