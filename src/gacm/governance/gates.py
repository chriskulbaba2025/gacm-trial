"""Fail-closed cumulative machine and authority-drift gates.

The gate functions consume durable observations; they do not treat caller prose,
environment defaults, or executor PASS claims as authority. A caller must provide
identity-bound evidence for every required boundary and an explicit drift ledger.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Mapping, Sequence


WHOLE_MACHINE_GATE_ID = "GACM-WHOLE-MACHINE-INTEGRITY-GATE"
DRIFT_GATE_ID = "GACM-INSTRUCTION-AND-AUTHORITY-DRIFT-GATE"
PROGRESSION_GATE_ID = "GACM-FOUNDATION-PROGRESSION-AND-ACCEPTANCE-SYNCHRONIZATION-GATE"
GATE_SCHEMA = "GACM_CUMULATIVE_GATES_V1"

DRIFT_FIELDS = (
    "application_sha",
    "governance_sha",
    "governing_specification",
    "foundation_id",
    "application_repository",
    "governance_repository",
    "authorized_application_branch",
    "authorized_governance_branch",
    "source_of_truth_files",
    "accepted_execution_contracts",
    "vendored_engine_authority",
    "graph_schema",
    "execution_recipe_schema",
    "provider_authority",
    "model_authority",
    "credential_authority",
    "external_service_authority",
    "allowed_surfaces",
    "forbidden_surfaces",
    "production_restrictions",
    "human_approval_requirements",
    "repair_limits",
    "acceptance_criteria",
    "required_proof_artifacts",
    "independent_verifier_requirements",
    "currentness_requirements",
    "previous_frozen_acceptance_id",
)

DRIFT_CLASSES = {
    "AUTHORIZED_CHANGE",
    "EXPECTED_DERIVED_CHANGE",
    "STALE_DEPENDENCY",
    "UNAUTHORIZED_CHANGE",
    "MISSING_AUTHORITY",
    "CONTRADICTION",
    "UNKNOWN",
}
BLOCKING_DRIFT_CLASSES = {
    "STALE_DEPENDENCY",
    "UNAUTHORIZED_CHANGE",
    "MISSING_AUTHORITY",
    "CONTRADICTION",
    "UNKNOWN",
}


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)


def _digest(value: Any) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


def _hex(value: Any, length: int) -> bool:
    return isinstance(value, str) and len(value) == length and all(char in "0123456789abcdef" for char in value.casefold())


@dataclass(frozen=True)
class GateDecision:
    gate_id: str
    status: str
    reasons: tuple[str, ...]
    evidence_digest: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "status": self.status,
            "reasons": list(self.reasons),
            "evidence_digest": self.evidence_digest,
        }


@dataclass(frozen=True)
class DriftCheck:
    decision: GateDecision
    ledger: tuple[dict[str, Any], ...]

    def to_dict(self) -> dict[str, Any]:
        return {"decision": self.decision.to_dict(), "ledger": [dict(item) for item in self.ledger]}


def _decision(gate_id: str, status: str, reasons: Sequence[str], evidence: Any = None) -> GateDecision:
    return GateDecision(gate_id, status, tuple(sorted(set(reasons))), None if evidence is None else _digest(evidence))


def _identity_matches(expected: Mapping[str, Any], evidence: Mapping[str, Any], reasons: list[str]) -> None:
    for key in ("application_sha", "governance_sha", "foundation_id", "application_repository", "governance_repository"):
        if key not in expected or key not in evidence:
            reasons.append(f"missing identity field: {key}")
        elif evidence[key] != expected[key]:
            reasons.append(f"identity mismatch: {key}")


def evaluate_whole_machine_integrity(
    expected: Mapping[str, Any],
    evidence: Mapping[str, Any] | None,
    required_boundaries: Sequence[str],
    required_connections: Sequence[str],
) -> GateDecision:
    """Evaluate cumulative runtime evidence for one exact candidate.

    The gate requires real observations for boundaries marked by the caller as
    required. Every observation must carry evidence identity and must explicitly
    reject synthetic/caller-asserted provenance. This is intentionally strict:
    missing evidence is not a PASS.
    """
    if not isinstance(expected, Mapping) or not isinstance(evidence, Mapping):
        return _decision(WHOLE_MACHINE_GATE_ID, "HOLD", ("whole-machine evidence is missing",), evidence)
    reasons: list[str] = []
    _identity_matches(expected, evidence, reasons)
    required_top = {
        "schema", "gate_id", "candidate_sha", "application_sha", "governance_sha",
        "foundation_id", "application_repository", "governance_repository", "execution_mode",
        "executor_evidence_authoritative", "boundaries", "connections", "prior_capabilities",
        "regression", "currentness", "independent_verification", "acceptance_state",
    }
    if set(evidence) != required_top:
        reasons.append("whole-machine evidence schema is incomplete or contains unknown fields")
    if evidence.get("schema") != GATE_SCHEMA:
        reasons.append("whole-machine evidence schema is unsupported")
    if evidence.get("gate_id") != WHOLE_MACHINE_GATE_ID:
        reasons.append("whole-machine gate identity is invalid")
    if evidence.get("candidate_sha") != expected.get("application_sha"):
        reasons.append("candidate SHA is not the expected application authority")
    if evidence.get("execution_mode") != "REAL_CONNECTED_RUNTIME":
        reasons.append("real connected runtime execution is required")
    if evidence.get("executor_evidence_authoritative") is not False:
        reasons.append("executor evidence must remain non-authoritative")

    boundaries = evidence.get("boundaries")
    seen: set[str] = set()
    if not isinstance(boundaries, list):
        reasons.append("boundary observations are missing")
    else:
        for boundary in boundaries:
            if not isinstance(boundary, Mapping) or set(boundary) != {"boundary_id", "status", "runtime_observed", "synthetic", "caller_asserted", "candidate_sha", "evidence_ids", "receipt_digest"}:
                reasons.append("boundary observation is malformed")
                continue
            boundary_id = boundary.get("boundary_id")
            seen.add(str(boundary_id))
            if boundary_id in required_boundaries and boundary.get("status") != "PASS":
                reasons.append(f"required boundary is not PASS: {boundary_id}")
            if boundary_id in required_boundaries and boundary.get("runtime_observed") is not True:
                reasons.append(f"required boundary lacks runtime observation: {boundary_id}")
            if boundary.get("synthetic") is not False or boundary.get("caller_asserted") is not False:
                reasons.append(f"synthetic or caller-asserted boundary evidence: {boundary_id}")
            if boundary.get("candidate_sha") != expected.get("application_sha"):
                reasons.append(f"boundary candidate identity mismatch: {boundary_id}")
            if not isinstance(boundary.get("evidence_ids"), list) or not boundary.get("evidence_ids"):
                reasons.append(f"boundary evidence identity missing: {boundary_id}")
            if not _hex(boundary.get("receipt_digest"), 64):
                reasons.append(f"boundary receipt digest invalid: {boundary_id}")
    for boundary_id in required_boundaries:
        if boundary_id not in seen:
            reasons.append(f"required boundary missing: {boundary_id}")

    connections = evidence.get("connections")
    connection_ids: set[str] = set()
    if not isinstance(connections, list):
        reasons.append("accepted-machine connections are missing")
    else:
        for connection in connections:
            if not isinstance(connection, Mapping) or set(connection) != {"connection_id", "status", "runtime_observed", "candidate_sha", "evidence_ids", "receipt_digest"}:
                reasons.append("connection observation is malformed")
                continue
            connection_id = str(connection.get("connection_id"))
            connection_ids.add(connection_id)
            if connection_id in required_connections and connection.get("status") != "PASS":
                reasons.append(f"required connection is not PASS: {connection_id}")
            if connection_id in required_connections and connection.get("runtime_observed") is not True:
                reasons.append(f"required connection lacks runtime observation: {connection_id}")
            if connection.get("candidate_sha") != expected.get("application_sha"):
                reasons.append(f"connection candidate identity mismatch: {connection_id}")
            if not isinstance(connection.get("evidence_ids"), list) or not connection.get("evidence_ids") or not _hex(connection.get("receipt_digest"), 64):
                reasons.append(f"connection evidence identity missing: {connection_id}")
    for connection_id in required_connections:
        if connection_id not in connection_ids:
            reasons.append(f"required connection missing: {connection_id}")

    prior = evidence.get("prior_capabilities")
    if not isinstance(prior, Mapping) or not prior or any(value != "PASS" for value in prior.values()):
        reasons.append("previously accepted capabilities are not cumulatively PASS")
    regression = evidence.get("regression")
    if (
        not isinstance(regression, Mapping)
        or set(regression) != {"status", "exact_candidate_sha", "previous_capabilities", "test_receipt_digest"}
        or regression.get("status") != "PASS"
        or regression.get("exact_candidate_sha") != expected.get("application_sha")
        or regression.get("previous_capabilities") != "PASS"
        or not _hex(regression.get("test_receipt_digest"), 64)
    ):
        reasons.append("whole-machine regression is missing, stale, or not PASS")
    currentness = evidence.get("currentness")
    if (
        not isinstance(currentness, Mapping)
        or set(currentness) != {
            "application_local_equals_remote", "governance_local_equals_remote",
            "application_main_unchanged", "governance_main_unchanged",
            "production_untouched", "evidence_ids", "receipt_digest",
        }
        or any(currentness.get(key) is not True for key in (
            "application_local_equals_remote", "governance_local_equals_remote",
            "application_main_unchanged", "governance_main_unchanged", "production_untouched",
        ))
        or not isinstance(currentness.get("evidence_ids"), list)
        or not currentness.get("evidence_ids")
        or not _hex(currentness.get("receipt_digest"), 64)
    ):
        reasons.append("currentness or protected-surface proof is incomplete")
    independent = evidence.get("independent_verification")
    if (
        not isinstance(independent, Mapping)
        or set(independent) != {
            "status", "derived_from_runtime_evidence", "trusts_executor_pass",
            "verifier_identity", "evidence_ids", "receipt_digest",
        }
        or independent.get("status") != "PASS"
        or independent.get("derived_from_runtime_evidence") is not True
        or independent.get("trusts_executor_pass") is not False
        or not isinstance(independent.get("verifier_identity"), str)
        or not independent.get("verifier_identity")
        or not isinstance(independent.get("evidence_ids"), list)
        or not independent.get("evidence_ids")
        or not _hex(independent.get("receipt_digest"), 64)
    ):
        reasons.append("independent verification is missing or trusts executor assertions")
    if evidence.get("acceptance_state") == "ACCEPTED" and regression.get("status") != "PASS":
        reasons.append("acceptance cannot precede whole-machine PASS")
    return _decision(WHOLE_MACHINE_GATE_ID, "PASS" if not reasons else "HOLD", reasons, evidence)


def evaluate_instruction_authority_drift(
    frozen: Mapping[str, Any] | None,
    observed: Mapping[str, Any] | None,
    ledger: Mapping[str, Mapping[str, Any]] | None,
) -> DriftCheck:
    """Compare a tranche against frozen authority using an explicit drift ledger."""
    reasons: list[str] = []
    rows: list[dict[str, Any]] = []
    if not isinstance(frozen, Mapping) or not isinstance(observed, Mapping) or not isinstance(ledger, Mapping):
        return DriftCheck(_decision(DRIFT_GATE_ID, "HOLD", ("frozen authority, observed authority, and drift ledger are required",), ledger), ())
    for field in DRIFT_FIELDS:
        if field not in frozen or field not in observed or field not in ledger:
            reasons.append(f"missing authority field or ledger row: {field}")
            continue
        row = ledger[field]
        if not isinstance(row, Mapping) or set(row) != {"frozen_value", "observed_value", "classification", "evidence_ids"}:
            reasons.append(f"malformed drift ledger row: {field}")
            continue
        classification = row.get("classification")
        if classification not in DRIFT_CLASSES and classification != "NO_DRIFT":
            reasons.append(f"unknown drift classification: {field}")
        if row.get("frozen_value") != frozen[field] or row.get("observed_value") != observed[field]:
            reasons.append(f"drift ledger does not reproduce source values: {field}")
        if not isinstance(row.get("evidence_ids"), list) or not row.get("evidence_ids"):
            reasons.append(f"drift evidence identity missing: {field}")
        differs = frozen[field] != observed[field]
        if not differs and classification != "NO_DRIFT":
            reasons.append(f"unchanged field is not explicitly classified NO_DRIFT: {field}")
        if differs and classification not in DRIFT_CLASSES:
            reasons.append(f"changed field lacks explicit classification: {field}")
        if differs and classification in BLOCKING_DRIFT_CLASSES:
            reasons.append(f"blocking authority drift: {field}={classification}")
        rows.append({"field": field, "frozen_value": frozen[field], "observed_value": observed[field], "classification": classification, "evidence_ids": list(row["evidence_ids"])})
    decision = _decision(DRIFT_GATE_ID, "PASS" if not reasons else "HOLD", reasons, rows)
    return DriftCheck(decision, tuple(rows))


def check_frozen_start(
    starting: Mapping[str, Any] | None,
    expected: Mapping[str, Any] | None,
) -> GateDecision:
    """Require a new foundation to begin from one accepted, exact SHA pair."""
    reasons: list[str] = []
    if not isinstance(starting, Mapping) or not isinstance(expected, Mapping):
        reasons.append("starting and expected frozen authority are required")
    else:
        for field in ("application_sha", "governance_sha", "application_repository", "governance_repository", "previous_acceptance_status"):
            if starting.get(field) != expected.get(field):
                reasons.append(f"frozen start mismatch: {field}")
        if starting.get("previous_acceptance_status") != "ACCEPTED":
            reasons.append("previous foundation is not accepted")
    return _decision("GACM-FROZEN-FOUNDATION-START-GATE", "PASS" if not reasons else "HOLD", reasons, starting)


def acceptance_readiness(
    whole_machine: GateDecision,
    drift: GateDecision,
    exact_candidate: bool,
    acceptance_pending: bool,
    progression: GateDecision | None = None,
) -> GateDecision:
    """Prevent acceptance or the next foundation from bypassing any mandatory gate."""
    reasons: list[str] = []
    if whole_machine.gate_id != WHOLE_MACHINE_GATE_ID or whole_machine.status != "PASS":
        reasons.append("whole-machine integrity gate is not PASS")
    if drift.gate_id != DRIFT_GATE_ID or drift.status != "PASS":
        reasons.append("instruction and authority drift gate is not PASS")
    if progression is None or progression.gate_id != PROGRESSION_GATE_ID or progression.status != "PASS":
        reasons.append("foundation progression and acceptance synchronization gate is not PASS")
    if exact_candidate is not True:
        reasons.append("candidate identity is not exact")
    if acceptance_pending is not True:
        reasons.append("acceptance state is not pending before closure")
    return _decision("GACM-FOUNDATION-ACCEPTANCE-READINESS-GATE", "PASS" if not reasons else "HOLD", reasons, {"whole_machine": whole_machine.to_dict(), "drift": drift.to_dict(), "progression": None if progression is None else progression.to_dict(), "exact_candidate": exact_candidate, "acceptance_pending": acceptance_pending})


def evaluate_progression_synchronization(
    previous_frozen_pair: Mapping[str, Any] | None,
    active_candidates: Sequence[Mapping[str, Any]] | None,
    qualification: Mapping[str, Any] | None,
    acceptance: Mapping[str, Any] | None,
    currentness: Mapping[str, Any] | None,
    next_foundation_started: bool = False,
) -> GateDecision:
    """Enforce one candidate, exact qualification/acceptance binding, and sequencing.

    This gate is deliberately receipt-oriented. It never treats a branch name,
    local working tree, or caller assertion as an application authority.
    """
    reasons: list[str] = []
    if not isinstance(previous_frozen_pair, Mapping):
        reasons.append("previous frozen application/governance pair is missing")
    else:
        for field in ("application_sha", "governance_sha", "application_repository", "governance_repository", "acceptance_status"):
            if not previous_frozen_pair.get(field):
                reasons.append(f"previous frozen pair missing: {field}")
        if previous_frozen_pair.get("acceptance_status") != "ACCEPTED":
            reasons.append("previous frozen pair is not accepted")

    candidates = list(active_candidates) if isinstance(active_candidates, Sequence) and not isinstance(active_candidates, (str, bytes)) else []
    authoritative = [item for item in candidates if isinstance(item, Mapping) and item.get("status") == "AUTHORITATIVE"]
    if len(authoritative) != 1:
        reasons.append("exactly one authoritative application candidate is required")
    if len(authoritative) > 1:
        reasons.append("more than one authoritative application candidate exists")
    candidate = authoritative[0] if len(authoritative) == 1 else {}
    candidate_sha = candidate.get("application_sha")
    if not _hex(candidate_sha, 40):
        reasons.append("authoritative candidate must declare an exact application SHA")
    for field in ("foundation_id", "application_repository", "application_branch"):
        if not candidate.get(field):
            reasons.append(f"authoritative candidate missing: {field}")
    if candidate.get("superseded") is True or candidate.get("status") == "SUPERSEDED":
        reasons.append("superseded candidate cannot be accepted")
    if isinstance(qualification, Mapping):
        if qualification.get("candidate_sha") != candidate_sha:
            reasons.append("qualification evidence does not bind to the authoritative candidate SHA")
        if qualification.get("status") != "PASS":
            reasons.append("qualification is not PASS")
        if qualification.get("invalidated") is True or qualification.get("mutation_after_qualification") is True:
            reasons.append("qualification was invalidated by a post-qualification mutation")
        if qualification.get("superseded") is True:
            reasons.append("qualification belongs to a superseded candidate")
        if qualification.get("evidence_current") is not True:
            reasons.append("qualification evidence is not current")
    else:
        reasons.append("qualification evidence is missing")
    if isinstance(acceptance, Mapping):
        if acceptance.get("status") != "ACCEPTED":
            reasons.append("governance acceptance is not ACCEPTED")
        if acceptance.get("application_sha") != candidate_sha:
            reasons.append("governance acceptance does not bind to the qualified application SHA")
        if acceptance.get("exact_sha_binding") is not True:
            reasons.append("governance acceptance lacks exact SHA binding")
        if not acceptance.get("governance_sha"):
            reasons.append("governance acceptance SHA is missing")
    else:
        reasons.append("governance acceptance is missing")
    if isinstance(currentness, Mapping):
        if currentness.get("application_local_equals_remote") is not True or currentness.get("governance_local_equals_remote") is not True:
            reasons.append("application and governance currentness are not proven")
    else:
        reasons.append("application and governance currentness evidence is missing")
    if next_foundation_started and not (
        isinstance(acceptance, Mapping)
        and acceptance.get("status") == "ACCEPTED"
        and acceptance.get("application_sha") == candidate_sha
        and acceptance.get("exact_sha_binding") is True
    ):
        reasons.append("next Foundation started before the current frozen pair existed")
    evidence = {
        "previous_frozen_pair": previous_frozen_pair,
        "active_candidates": candidates,
        "qualification": qualification,
        "acceptance": acceptance,
        "currentness": currentness,
        "next_foundation_started": next_foundation_started,
    }
    return _decision(PROGRESSION_GATE_ID, "PASS" if not reasons else "HOLD", reasons, evidence)
