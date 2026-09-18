"""Deterministic promotion eligibility checks."""

from __future__ import annotations

from typing import Any, Mapping

from .models import EligibilityResult, PromotionState


class PromotionEligibility:
    def evaluate(self, evidence: Mapping[str, Any]) -> EligibilityResult:
        reasons: list[str] = []
        blocked: list[str] = []
        if evidence.get("github_authority_status") != "VERIFIED": reasons.append("GITHUB_AUTHORITY_NOT_VERIFIED")
        if evidence.get("operational_context_status") != "VERIFIED": reasons.append("OPERATIONAL_CONTEXT_NOT_VERIFIED")
        if evidence.get("execution_status") != "COMPLETED": reasons.append("EXECUTION_NOT_COMPLETED")
        qualification = evidence.get("qualification", {})
        pre = qualification.get("pre_promotion", {}) if isinstance(qualification, Mapping) else {}
        graph = qualification.get("graph", {}) if isinstance(qualification, Mapping) else {}
        if pre.get("ready") is not True: reasons.append("FINITE_QUALIFICATION_NOT_COMPLETE")
        if not graph.get("graph_digest") or not graph.get("spec_digest") or not graph.get("denominator"):
            reasons.append("FROZEN_QUALIFICATION_IDENTITY_REQUIRED")
        identity = evidence.get("identity_validation_result", evidence.get("placeholder_identity_result", "VALID"))
        if identity != "VALID": reasons.append("IDENTITY_VALIDATION_NOT_VALID")
        verifier = evidence.get("verification", {})
        if not isinstance(verifier, Mapping) or verifier.get("status") != "PASS" or verifier.get("authoritative") is not True or verifier.get("issuer_role") != "INDEPENDENT_VERIFIER": reasons.append("AUTHORITATIVE_VERIFIER_PASS_REQUIRED")
        if evidence.get("unresolved_blocked") or evidence.get("blocked_condition"): blocked.append("UNRESOLVED_BLOCKED_CONDITION")
        if evidence.get("repair_required") or evidence.get("requalification_required"): reasons.append("REPAIR_OR_REQUALIFICATION_INCOMPLETE")
        if not evidence.get("rollback_target_sha"): reasons.append("ROLLBACK_TARGET_REQUIRED")
        if not evidence.get("candidate_sha") or not evidence.get("candidate_artifact_identity"): reasons.append("EXACT_CANDIDATE_IDENTITY_REQUIRED")
        if evidence.get("candidate_identity_matches") is False: reasons.append("CANDIDATE_IDENTITY_MISMATCH")
        if evidence.get("authority_continuity") is False: blocked.append("CURRENT_AUTHORITY_CHANGED_SINCE_VERIFICATION")
        if evidence.get("human_approval_required") and not evidence.get("human_approval"): reasons.append("REQUIRED_HUMAN_APPROVAL_MISSING")
        if blocked: reasons.extend(blocked); return EligibilityResult(PromotionState.BLOCKED.value, tuple(sorted(set(reasons))))
        return EligibilityResult(PromotionState.ELIGIBLE.value if not reasons else PromotionState.NOT_ELIGIBLE.value, tuple(sorted(set(reasons))))
