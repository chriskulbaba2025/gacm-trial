from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gacm.governance import (  # noqa: E402
    DRIFT_FIELDS,
    DRIFT_GATE_ID,
    WHOLE_MACHINE_GATE_ID,
    acceptance_readiness,
    check_frozen_start,
    evaluate_instruction_authority_drift,
    evaluate_whole_machine_integrity,
)


APP = "a" * 40
GOV = "b" * 40


def expected():
    return {
        "application_sha": APP,
        "governance_sha": GOV,
        "foundation_id": "F15",
        "application_repository": "application/repo",
        "governance_repository": "governance/repo",
    }


def machine_evidence():
    boundaries = [
        "authority", "currentness", "context", "graph", "work_unit", "recipe",
        "routing", "action_authorization", "gcu", "real_executor", "evidence",
        "verification", "persistence", "governance_acceptance",
    ]
    connections = [
        "authority-to-currentness", "graph-to-work-unit", "work-unit-to-executor",
        "executor-to-evidence", "evidence-to-verification", "verification-to-acceptance",
    ]
    return {
        "schema": "GACM_CUMULATIVE_GATES_V1",
        "gate_id": WHOLE_MACHINE_GATE_ID,
        "candidate_sha": APP,
        **expected(),
        "execution_mode": "REAL_CONNECTED_RUNTIME",
        "executor_evidence_authoritative": False,
        "boundaries": [
            {"boundary_id": item, "status": "PASS", "runtime_observed": True, "synthetic": False, "caller_asserted": False, "candidate_sha": APP, "evidence_ids": [f"ev-{item}"], "receipt_digest": "c" * 64}
            for item in boundaries
        ],
        "connections": [
            {"connection_id": item, "status": "PASS", "runtime_observed": True, "candidate_sha": APP, "evidence_ids": [f"ev-{item}"], "receipt_digest": "d" * 64}
            for item in connections
        ],
        "prior_capabilities": {"F1": "PASS", "F13": "PASS", "F14": "PASS"},
        "regression": {"status": "PASS", "exact_candidate_sha": APP, "previous_capabilities": "PASS", "test_receipt_digest": "e" * 64},
        "currentness": {"application_local_equals_remote": True, "governance_local_equals_remote": True, "application_main_unchanged": True, "governance_main_unchanged": True, "production_untouched": True, "evidence_ids": ["currentness-receipt"], "receipt_digest": "f" * 64},
        "independent_verification": {"status": "PASS", "derived_from_runtime_evidence": True, "trusts_executor_pass": False, "verifier_identity": "independent-verifier", "evidence_ids": ["verification-receipt"], "receipt_digest": "1" * 64},
        "acceptance_state": "PENDING",
    }


def drift_inputs():
    frozen = {field: f"frozen-{field}" for field in DRIFT_FIELDS}
    observed = copy.deepcopy(frozen)
    ledger = {field: {"frozen_value": frozen[field], "observed_value": observed[field], "classification": "NO_DRIFT", "evidence_ids": [f"ev-{field}"]} for field in DRIFT_FIELDS}
    return frozen, observed, ledger


class CumulativeGovernanceGateTests(unittest.TestCase):
    def test_real_cumulative_machine_passes_exact_candidate(self):
        required_boundaries = [item["boundary_id"] for item in machine_evidence()["boundaries"]]
        required_connections = [item["connection_id"] for item in machine_evidence()["connections"]]
        result = evaluate_whole_machine_integrity(expected(), machine_evidence(), required_boundaries, required_connections)
        self.assertEqual("PASS", result.status)

    def test_missing_prior_capability_fails_closed(self):
        evidence = machine_evidence()
        evidence["prior_capabilities"]["F13"] = "UNKNOWN"
        result = evaluate_whole_machine_integrity(expected(), evidence, [item["boundary_id"] for item in evidence["boundaries"]], [item["connection_id"] for item in evidence["connections"]])
        self.assertEqual("HOLD", result.status)

    def test_synthetic_runtime_receipt_fails_closed(self):
        evidence = machine_evidence()
        evidence["boundaries"][0]["synthetic"] = True
        result = evaluate_whole_machine_integrity(expected(), evidence, [item["boundary_id"] for item in evidence["boundaries"]], [item["connection_id"] for item in evidence["connections"]])
        self.assertEqual("HOLD", result.status)

    def test_candidate_mismatch_fails_closed(self):
        evidence = machine_evidence()
        evidence["regression"]["exact_candidate_sha"] = "e" * 40
        result = evaluate_whole_machine_integrity(expected(), evidence, [item["boundary_id"] for item in evidence["boundaries"]], [item["connection_id"] for item in evidence["connections"]])
        self.assertEqual("HOLD", result.status)

    def test_missing_connection_fails_closed(self):
        evidence = machine_evidence()
        evidence["connections"] = evidence["connections"][:-1]
        result = evaluate_whole_machine_integrity(expected(), evidence, [item["boundary_id"] for item in evidence["boundaries"]], [item["connection_id"] for item in machine_evidence()["connections"]])
        self.assertEqual("HOLD", result.status)

    def test_authority_drift_no_change_passes_with_explicit_ledger(self):
        frozen, observed, ledger = drift_inputs()
        result = evaluate_instruction_authority_drift(frozen, observed, ledger)
        self.assertEqual(DRIFT_GATE_ID, result.decision.gate_id)
        self.assertEqual("PASS", result.decision.status)

    def test_stale_dependency_blocks_before_execution(self):
        frozen, observed, ledger = drift_inputs()
        observed["vendored_engine_authority"] = "stale"
        ledger["vendored_engine_authority"]["observed_value"] = "stale"
        ledger["vendored_engine_authority"]["classification"] = "STALE_DEPENDENCY"
        result = evaluate_instruction_authority_drift(frozen, observed, ledger)
        self.assertEqual("HOLD", result.decision.status)

    def test_unknown_drift_classification_blocks(self):
        frozen, observed, ledger = drift_inputs()
        observed["model_authority"] = "changed"
        ledger["model_authority"]["observed_value"] = "changed"
        ledger["model_authority"]["classification"] = "INFERRED"
        result = evaluate_instruction_authority_drift(frozen, observed, ledger)
        self.assertEqual("HOLD", result.decision.status)

    def test_missing_authority_field_blocks(self):
        frozen, observed, ledger = drift_inputs()
        del ledger["provider_authority"]
        result = evaluate_instruction_authority_drift(frozen, observed, ledger)
        self.assertEqual("HOLD", result.decision.status)

    def test_frozen_start_requires_exact_previous_acceptance(self):
        start = {"application_sha": APP, "governance_sha": GOV, "application_repository": "application/repo", "governance_repository": "governance/repo", "previous_acceptance_status": "ACCEPTED"}
        result = check_frozen_start(start, start)
        self.assertEqual("PASS", result.status)
        start["governance_sha"] = "f" * 40
        self.assertEqual("HOLD", check_frozen_start(start, {**start, "governance_sha": GOV}).status)

    def test_acceptance_cannot_bypass_failed_machine_or_drift_gate(self):
        machine = evaluate_whole_machine_integrity(expected(), machine_evidence(), [], [])
        _, _, ledger = drift_inputs()
        frozen, observed, _ = drift_inputs()
        observed["foundation_id"] = "F14"
        ledger["foundation_id"]["observed_value"] = "F14"
        ledger["foundation_id"]["classification"] = "CONTRADICTION"
        drift = evaluate_instruction_authority_drift(frozen, observed, ledger).decision
        result = acceptance_readiness(machine, drift, True, True)
        self.assertEqual("HOLD", result.status)

    def test_next_foundation_pending_acceptance_is_not_authorized(self):
        machine = evaluate_whole_machine_integrity(expected(), machine_evidence(), ["authority"], ["authority-to-currentness"])
        frozen, observed, ledger = drift_inputs()
        drift = evaluate_instruction_authority_drift(frozen, observed, ledger).decision
        result = acceptance_readiness(machine, drift, True, False)
        self.assertEqual("HOLD", result.status)


if __name__ == "__main__":
    unittest.main()
