"""Independent deterministic verification engine."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Callable

from .checks import (
    check_context,
    check_executor_claim,
    check_paths,
    check_repository_identity,
    check_routing,
    check_tests,
)
from .graph_release import check_graph_release
from .models import VerificationInput, VerificationReceipt, VerificationStatus, canonical
from .scope import determine_scope


class IndependentVerificationEngine:
    """Issue PASS only after independent evidence satisfies every check."""

    def __init__(self, verifier_identity: str = "gacm-independent-verifier-v1", clock: Callable[[], str] | None = None):
        self.verifier_identity = verifier_identity
        self.clock = clock or (lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    def verify(self, inputs: VerificationInput) -> VerificationReceipt:
        started_at = self.clock()
        contract = inputs.work_unit_contract
        receipt = inputs.execution_receipt
        reasons: list[str] = []
        evidence_reviewed = ["run_state", "work_unit_contract", "execution_receipt"]

        if not inputs.run_state or not contract or not receipt:
            return self._receipt(inputs, VerificationStatus.BLOCKED, started_at, evidence_reviewed, reasons + ["required verification input is missing"])
        if inputs.run_state.get("run_id") != contract.get("run_id") or receipt.get("run_id") != contract.get("run_id"):
            reasons.append("run identity mismatch")
        if receipt.get("work_unit_id") != contract.get("work_unit_id"):
            reasons.append("work-unit identity mismatch")
        if receipt.get("execution_status") not in {"COMPLETED", "FAILED", "BLOCKED", "STOPPED"}:
            reasons.append("execution receipt has no valid execution status")
        elif receipt.get("execution_status") != "COMPLETED":
            reasons.append("execution did not complete successfully")
        if inputs.diff_evidence is None:
            reasons.append("independent diff evidence is unavailable")
        if inputs.actual_changed_paths is None:
            reasons.append("independent changed-path observation is unavailable")

        authority_status, authority_reasons = check_repository_identity(contract, receipt, inputs.starting_repository, inputs.ending_repository)
        path_status, path_reasons = check_paths(inputs.actual_changed_paths, inputs.allowed_writable_surfaces, inputs.forbidden_surfaces)
        context_status, context_reasons = check_context(contract, inputs.operational_context)
        routing_status, routing_reasons = check_routing(contract, inputs.routing_decision, receipt)
        regression_status, regression_reasons = check_tests(contract, inputs.test_contract, inputs.test_outcomes, inputs.ending_repository.get("sha"))
        claim_status, claim_reasons = check_executor_claim(receipt)
        outcome_status, outcome_reasons = self._check_outcome(inputs)
        graph_release = check_graph_release(contract, inputs.graph_release_evidence)
        graph_release_reasons = list(graph_release.reasons)
        reasons.extend(authority_reasons + path_reasons + context_reasons + routing_reasons + regression_reasons + claim_reasons + outcome_reasons + graph_release_reasons)
        if graph_release.status != "NOT_APPLICABLE":
            evidence_reviewed.append("graph_release_evidence")

        changed = inputs.actual_changed_paths
        scope = determine_scope(
            changed or (), inputs.scope_patterns, inputs.dependency_paths, inputs.prior_assurance
        )
        if changed is None:
            scope = scope.__class__(
                classification="UNKNOWN",
                changed_paths=(),
                affected_scope=(),
                broader_requalification_required=True,
                requalification_reasons=("NO_INDEPENDENT_DIFF",),
                prior_assurance_invalidated=tuple(str(item.get("assurance_id", "")) for item in inputs.prior_assurance),
                prior_assurance_preserved=(),
                rerun_scope=(),
            )

        if receipt.get("files_changed") is not None and changed is not None:
            if tuple(sorted(set(receipt.get("files_changed", ())))) != tuple(sorted(set(changed))):
                reasons.append("executor changed-file claim disagrees with independently observed Git diff")
        if scope.classification == "UNKNOWN":
            reasons.append("blast radius cannot be determined independently")

        statuses = [authority_status, path_status, context_status, routing_status, regression_status, claim_status, outcome_status]
        if graph_release.status != "NOT_APPLICABLE":
            statuses.append(graph_release.status)
        if any(item == "FAIL" for item in statuses):
            status = VerificationStatus.FAIL
        elif any(item == "UNOBSERVABLE" for item in statuses) or inputs.actual_changed_paths is None or inputs.diff_evidence is None:
            status = VerificationStatus.UNOBSERVABLE
        elif any(item == "BLOCKED" for item in statuses) or scope.classification == "UNKNOWN":
            status = VerificationStatus.BLOCKED
        elif reasons:
            status = VerificationStatus.FAIL
        else:
            status = VerificationStatus.PASS

        return self._receipt(
            inputs,
            status,
            started_at,
            evidence_reviewed + (["diff_evidence"] if inputs.diff_evidence is not None else []),
            reasons,
            scope=scope,
            expected=outcome_status,
            writable=path_status,
            forbidden=path_status,
            regression=regression_status,
            authority=authority_status,
            context=context_status,
            routing=routing_status,
            graph_release=graph_release.status,
            graph_release_digest=graph_release.evidence_digest,
        )

    @staticmethod
    def _check_outcome(inputs: VerificationInput) -> tuple[str, list[str]]:
        if inputs.expected_outcome_met is None:
            return "UNOBSERVABLE", ["expected outcome cannot be independently observed"]
        if inputs.expected_outcome_met is False:
            return "FAIL", ["expected outcome was not met"]
        return "PASS", []

    def _receipt(
        self,
        inputs: VerificationInput,
        status: VerificationStatus,
        started_at: str,
        evidence_reviewed: list[str],
        reasons: list[str],
        scope=None,
        expected="UNOBSERVABLE",
        writable="UNOBSERVABLE",
        forbidden="UNOBSERVABLE",
        regression="UNOBSERVABLE",
        authority="UNOBSERVABLE",
        context="UNOBSERVABLE",
        routing="UNOBSERVABLE",
        graph_release="NOT_APPLICABLE",
        graph_release_digest=None,
    ) -> VerificationReceipt:
        scope_dict = scope.to_dict() if scope is not None else {
            "classification": "UNKNOWN", "changed_paths": [], "affected_scope": [],
            "broader_requalification_required": True, "requalification_reasons": [],
            "prior_assurance_invalidated": [], "prior_assurance_preserved": [], "rerun_scope": [],
        }
        material = {
            "run_id": inputs.work_unit_contract.get("run_id"),
            "work_unit_id": inputs.work_unit_contract.get("work_unit_id"),
            "status": status.value,
            "scope": scope_dict,
            "reasons": sorted(set(reasons)),
            "graph_release_result": graph_release,
            "graph_release_evidence_digest": graph_release_digest,
        }
        verification_id = "verify-" + hashlib.sha256(canonical(material).encode("utf-8")).hexdigest()[:24]
        return VerificationReceipt(
            run_id=str(inputs.work_unit_contract.get("run_id", "unknown")),
            work_unit_id=str(inputs.work_unit_contract.get("work_unit_id", "unknown")),
            verification_id=verification_id,
            verifier_identity=self.verifier_identity,
            status=status.value,
            evidence_reviewed=tuple(evidence_reviewed),
            scope_checked=tuple(scope_dict.get("changed_paths", [])),
            expected_outcome_result=expected,
            writable_surface_result=writable,
            forbidden_surface_result=forbidden,
            regression_result=regression,
            authority_integrity_result=authority,
            operational_context_result=context,
            model_routing_integrity_result=routing,
            graph_release_result=graph_release,
            graph_release_evidence_digest=graph_release_digest,
            affected_scope_determination=scope_dict,
            prior_assurance_invalidated=tuple(scope_dict.get("prior_assurance_invalidated", [])),
            prior_assurance_preserved=tuple(scope_dict.get("prior_assurance_preserved", [])),
            broader_requalification_required=bool(scope_dict.get("broader_requalification_required")),
            reasons=tuple(sorted(set(reasons))),
            started_at=started_at,
            completed_at=self.clock(),
            authoritative=status == VerificationStatus.PASS,
            issuer_role="INDEPENDENT_VERIFIER",
        )
