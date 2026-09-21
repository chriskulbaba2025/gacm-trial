"""Fail-closed generalization and whole-system acceptance gate."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Mapping

GATE_ID = "GACM-GENERALIZATION-AND-WHOLE-SYSTEM-GATE"
FIXTURE_TARGET_COLLAPSE = "FIXTURE_TARGET_COLLAPSE"
SEQUENTIAL_BLOCKER_TUNNELING = "SEQUENTIAL_BLOCKER_TUNNELING"


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)


class GeneralizationGateStatus(StrEnum):
    PASS = "PASS"
    HOLD = "HOLD"
    AUTHORIZED_FIXTURE_SPECIFIC = "AUTHORIZED_FIXTURE_SPECIFIC"


@dataclass(frozen=True)
class GeneralizationGateResult:
    gate_id: str
    status: str
    contract_digest: str
    reasons: tuple[str, ...]
    escape_classes: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    scenario_ids: tuple[str, ...]
    runtime_path_identity: str | None
    authoritative: bool
    issuer_role: str = "GACM_GOVERNANCE"
    fixture_specific_authorized: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "status": self.status,
            "contract_digest": self.contract_digest,
            "reasons": list(self.reasons),
            "escape_classes": list(self.escape_classes),
            "evidence_ids": list(self.evidence_ids),
            "scenario_ids": list(self.scenario_ids),
            "runtime_path_identity": self.runtime_path_identity,
            "authoritative": self.authoritative,
            "issuer_role": self.issuer_role,
            "fixture_specific_authorized": self.fixture_specific_authorized,
        }

    def content_sha(self) -> str:
        return hashlib.sha256(canonical(self.to_dict()).encode("utf-8")).hexdigest()[:40]


class GeneralizationGate:
    """Machine gate preventing fixture-target collapse and sequential blocker tunneling."""

    accepted_statuses = {
        GeneralizationGateStatus.PASS.value,
        GeneralizationGateStatus.AUTHORIZED_FIXTURE_SPECIFIC.value,
    }

    @staticmethod
    def contract_digest(contract: Mapping[str, Any]) -> str:
        return hashlib.sha256(canonical(contract).encode("utf-8")).hexdigest()[:40]

    def preflight(self, contract: Mapping[str, Any] | None) -> GeneralizationGateResult:
        contract = contract if isinstance(contract, Mapping) else {}
        reasons: list[str] = []
        escapes: set[str] = set()
        evidence_ids: set[str] = set()
        mode = str(contract.get("mode", ""))
        if contract.get("gate_id") != GATE_ID:
            reasons.append("GENERALIZATION_GATE_ID_MISSING_OR_INVALID")
        if mode not in {"GENERALIZED", "FIXTURE_SPECIFIC_AUTHORIZED"}:
            reasons.append("GENERALIZATION_GATE_MODE_INVALID")
        if not str(contract.get("product_definition_of_done", "")).strip():
            reasons.append("PRODUCT_LEVEL_DEFINITION_OF_DONE_MISSING")
            escapes.add(FIXTURE_TARGET_COLLAPSE)
        scope = tuple(str(x).strip() for x in contract.get("authorized_capability_scope", ()) if str(x).strip())
        if not scope:
            reasons.append("AUTHORIZED_CAPABILITY_SCOPE_MISSING")
        connected = tuple(str(x).strip() for x in contract.get("connected_system_path", ()) if str(x).strip())
        if len(connected) < 2:
            reasons.append("CONNECTED_SYSTEM_MAP_MISSING")
            escapes.add(SEQUENTIAL_BLOCKER_TUNNELING)
        required_boundaries = tuple(str(x).strip() for x in contract.get("required_full_path_boundaries", ()) if str(x).strip())
        if not required_boundaries:
            reasons.append("FULL_PATH_BOUNDARY_CONTRACT_MISSING")
        elif connected and any(item not in connected for item in required_boundaries):
            reasons.append("FULL_PATH_BOUNDARY_OUTSIDE_CONNECTED_SYSTEM_MAP")
        if mode == "GENERALIZED":
            minimum = contract.get("minimum_fresh_scenarios", 2)
            if not isinstance(minimum, int) or minimum < 2:
                reasons.append("MINIMUM_FRESH_SCENARIOS_MUST_BE_AT_LEAST_TWO")
                escapes.add(FIXTURE_TARGET_COLLAPSE)
        elif mode == "FIXTURE_SPECIFIC_AUTHORIZED":
            auth = contract.get("fixture_specific_authorization")
            if not isinstance(auth, Mapping):
                reasons.append("FIXTURE_SPECIFIC_AUTHORIZATION_MISSING")
            else:
                if auth.get("authorized_by") not in {"HUMAN", "GACM_GOVERNANCE", "RELEASE_AUTHORITY"}:
                    reasons.append("FIXTURE_SPECIFIC_AUTHORIZER_INVALID")
                if not str(auth.get("reason", "")).strip() or not str(auth.get("evidence_id", "")).strip():
                    reasons.append("FIXTURE_SPECIFIC_AUTHORIZATION_INCOMPLETE")
                else:
                    evidence_ids.add(str(auth["evidence_id"]))
        status = GeneralizationGateStatus.HOLD.value if reasons else (
            GeneralizationGateStatus.AUTHORIZED_FIXTURE_SPECIFIC.value
            if mode == "FIXTURE_SPECIFIC_AUTHORIZED" else GeneralizationGateStatus.PASS.value
        )
        return GeneralizationGateResult(
            GATE_ID,
            status,
            self.contract_digest(contract),
            tuple(sorted(set(reasons))),
            tuple(sorted(escapes)),
            tuple(sorted(evidence_ids)),
            (),
            None,
            status in self.accepted_statuses,
            fixture_specific_authorized=status == GeneralizationGateStatus.AUTHORIZED_FIXTURE_SPECIFIC.value,
        )

    def evaluate(self, contract: Mapping[str, Any] | None, evidence: Mapping[str, Any] | None) -> GeneralizationGateResult:
        preflight = self.preflight(contract)
        if preflight.status == GeneralizationGateStatus.HOLD.value:
            return preflight
        contract = contract if isinstance(contract, Mapping) else {}
        evidence = evidence if isinstance(evidence, Mapping) else {}
        reasons: list[str] = []
        escapes: set[str] = set()
        evidence_ids: set[str] = set(preflight.evidence_ids)
        digest = self.contract_digest(contract)

        if evidence.get("issuer_role") != "INDEPENDENT_VERIFIER" or evidence.get("authoritative") is not True:
            reasons.append("INDEPENDENT_GENERALIZATION_EVIDENCE_REQUIRED")
        if evidence.get("contract_digest") != digest:
            reasons.append("FROZEN_ACCEPTANCE_BOUNDARY_DIGEST_MISMATCH")
            escapes.add(SEQUENTIAL_BLOCKER_TUNNELING)
        if evidence.get("acceptance_boundary_unchanged") is not True:
            reasons.append("ACCEPTANCE_BOUNDARY_WAS_NARROWED_OR_UNPROVEN")
            escapes.add(FIXTURE_TARGET_COLLAPSE)
        if evidence.get("system_map_status") != "PASS":
            reasons.append("CONNECTED_SYSTEM_AUDIT_NOT_PROVEN")
            escapes.add(SEQUENTIAL_BLOCKER_TUNNELING)
        if evidence.get("whole_authorized_scope_closed") is not True:
            reasons.append("WHOLE_AUTHORIZED_SCOPE_NOT_CLOSED")
            escapes.add(SEQUENTIAL_BLOCKER_TUNNELING)
        if evidence.get("closure_definition_of_done_met") is not True:
            reasons.append("PRODUCT_LEVEL_DEFINITION_OF_DONE_NOT_PROVEN")
            escapes.add(FIXTURE_TARGET_COLLAPSE)

        evidence_ids.update(self._ids(evidence.get("evidence_ids")))
        mode = str(contract.get("mode", ""))
        if mode == "FIXTURE_SPECIFIC_AUTHORIZED":
            ref = evidence.get("reference_regression")
            if not isinstance(ref, Mapping) or ref.get("status") != "PASS":
                reasons.append("AUTHORIZED_FIXTURE_REFERENCE_REGRESSION_NOT_PROVEN")
            else:
                evidence_ids.update(self._ids(ref.get("evidence_ids")))
            status = GeneralizationGateStatus.HOLD.value if reasons else GeneralizationGateStatus.AUTHORIZED_FIXTURE_SPECIFIC.value
            return GeneralizationGateResult(
                GATE_ID, status, digest, tuple(sorted(set(reasons))), tuple(sorted(escapes)),
                tuple(sorted(evidence_ids)), (), None, status in self.accepted_statuses,
                fixture_specific_authorized=status == GeneralizationGateStatus.AUTHORIZED_FIXTURE_SPECIFIC.value,
            )

        required_boundaries = tuple(str(x) for x in contract.get("required_full_path_boundaries", ()))
        minimum = int(contract.get("minimum_fresh_scenarios", 2))
        reference_ids = {str(x) for x in contract.get("reference_regression_ids", ())}
        scenarios = evidence.get("generalized_scenarios")
        scenario_ids: list[str] = []
        runtime_paths: set[str] = set()
        input_ids: set[str] = set()
        if not isinstance(scenarios, (list, tuple)) or len(scenarios) < minimum:
            reasons.append("GENERALIZED_SCENARIOS_MISSING_OR_INSUFFICIENT")
            escapes.add(FIXTURE_TARGET_COLLAPSE)
            scenarios = []
        for raw in scenarios:
            scenario = raw if isinstance(raw, Mapping) else {}
            sid = str(scenario.get("scenario_id", ""))
            if not sid:
                reasons.append("GENERALIZED_SCENARIO_ID_MISSING")
                continue
            scenario_ids.append(sid)
            if sid in reference_ids or scenario.get("reference_fixture") is True:
                reasons.append(f"GENERALIZED_SCENARIO_IS_REFERENCE_FIXTURE:{sid}")
                escapes.add(FIXTURE_TARGET_COLLAPSE)
            if scenario.get("materially_different") is not True:
                reasons.append(f"GENERALIZED_SCENARIO_NOT_MATERIALLY_DIFFERENT:{sid}")
                escapes.add(FIXTURE_TARGET_COLLAPSE)
            input_identity = str(scenario.get("input_identity", ""))
            if not input_identity:
                reasons.append(f"GENERALIZED_SCENARIO_INPUT_IDENTITY_MISSING:{sid}")
            else:
                input_ids.add(input_identity)
            path_identity = str(scenario.get("runtime_path_identity", ""))
            if not path_identity:
                reasons.append(f"GENERIC_RUNTIME_PATH_IDENTITY_MISSING:{sid}")
            else:
                runtime_paths.add(path_identity)
            boundary_results = scenario.get("boundary_results")
            if not isinstance(boundary_results, Mapping):
                reasons.append(f"FULL_PATH_RESULTS_MISSING:{sid}")
            else:
                for boundary in required_boundaries:
                    if boundary_results.get(boundary) != "PASS":
                        reasons.append(f"FULL_PATH_BOUNDARY_NOT_PROVEN:{sid}:{boundary}")
            ids = self._ids(scenario.get("evidence_ids"))
            if not ids:
                reasons.append(f"GENERALIZED_SCENARIO_EVIDENCE_MISSING:{sid}")
            evidence_ids.update(ids)
        if scenarios and len(input_ids) < minimum:
            reasons.append("FRESH_INPUT_IDENTITIES_NOT_DISTINCT")
            escapes.add(FIXTURE_TARGET_COLLAPSE)
        if len(runtime_paths) != 1:
            reasons.append("GENERALIZED_SCENARIOS_DID_NOT_PROVE_ONE_GENERIC_RUNTIME_PATH")
            escapes.add(FIXTURE_TARGET_COLLAPSE)

        scan = evidence.get("fixture_dependency_scan")
        if not isinstance(scan, Mapping) or scan.get("status") != "PASS" or not scan.get("scanner_id") or not scan.get("scanned_paths"):
            reasons.append("FIXTURE_DEPENDENCY_SCAN_NOT_PROVEN")
            escapes.add(FIXTURE_TARGET_COLLAPSE)
        else:
            if scan.get("findings", ()):
                reasons.append("FIXTURE_SPECIFIC_RUNTIME_DEPENDENCY_DETECTED")
                escapes.add(FIXTURE_TARGET_COLLAPSE)
            evidence_ids.update(self._ids(scan.get("evidence_ids")))

        reference_regression = evidence.get("reference_regression")
        if reference_ids:
            if not isinstance(reference_regression, Mapping) or reference_regression.get("status") != "PASS":
                reasons.append("REFERENCE_REGRESSION_NOT_PROVEN_SEPARATELY")
            else:
                evidence_ids.update(self._ids(reference_regression.get("evidence_ids")))

        for key, required_key in (("continuity_results", "required_continuity_controls"), ("security_results", "required_security_controls")):
            results = evidence.get(key)
            for control in contract.get(required_key, ()):
                if not isinstance(results, Mapping) or results.get(str(control)) != "PASS":
                    reasons.append(f"REQUIRED_CONTROL_NOT_PROVEN:{control}")

        full_regression = evidence.get("full_regression")
        if not isinstance(full_regression, Mapping) or full_regression.get("status") != "PASS":
            reasons.append("FULL_REGRESSION_NOT_PROVEN")
        else:
            evidence_ids.update(self._ids(full_regression.get("evidence_ids")))

        status = GeneralizationGateStatus.HOLD.value if reasons else GeneralizationGateStatus.PASS.value
        return GeneralizationGateResult(
            GATE_ID, status, digest, tuple(sorted(set(reasons))), tuple(sorted(escapes)),
            tuple(sorted(evidence_ids)), tuple(sorted(set(scenario_ids))),
            next(iter(runtime_paths)) if len(runtime_paths) == 1 else None,
            status in self.accepted_statuses,
        )

    @staticmethod
    def _ids(value: Any) -> set[str]:
        if not isinstance(value, (list, tuple, set)):
            return set()
        return {str(item) for item in value if str(item)}
