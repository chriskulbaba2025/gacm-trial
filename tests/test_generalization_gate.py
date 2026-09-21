import unittest

from gacm.generalization import (
    FIXTURE_TARGET_COLLAPSE,
    GATE_ID,
    SEQUENTIAL_BLOCKER_TUNNELING,
    GeneralizationGate,
    scan_runtime_fixture_dependencies,
)


def contract(**overrides):
    value = {
        "gate_id": GATE_ID,
        "mode": "GENERALIZED",
        "product_definition_of_done": "Variable valid inputs traverse the product capability to durable downstream output.",
        "authorized_capability_scope": ["capability"],
        "connected_system_path": ["input", "processing", "decision", "persistence", "reopen", "output"],
        "required_full_path_boundaries": ["input", "processing", "decision", "persistence", "reopen", "output"],
        "minimum_fresh_scenarios": 2,
        "reference_regression_ids": ["reference-case"],
        "required_continuity_controls": ["save_reopen", "downstream_continuity"],
        "required_security_controls": ["cross_run_isolation"],
    }
    value.update(overrides)
    return value


def evidence(c, **overrides):
    gate = GeneralizationGate()
    boundaries = c["required_full_path_boundaries"]
    value = {
        "issuer_role": "INDEPENDENT_VERIFIER",
        "authoritative": True,
        "contract_digest": gate.contract_digest(c),
        "acceptance_boundary_unchanged": True,
        "system_map_status": "PASS",
        "whole_authorized_scope_closed": True,
        "closure_definition_of_done_met": True,
        "generalized_scenarios": [
            {
                "scenario_id": "fresh-a",
                "input_identity": "input-a",
                "materially_different": True,
                "reference_fixture": False,
                "runtime_path_identity": "generic-runtime-v1",
                "boundary_results": {name: "PASS" for name in boundaries},
                "evidence_ids": ["fresh-a-proof"],
            },
            {
                "scenario_id": "fresh-b",
                "input_identity": "input-b",
                "materially_different": True,
                "reference_fixture": False,
                "runtime_path_identity": "generic-runtime-v1",
                "boundary_results": {name: "PASS" for name in boundaries},
                "evidence_ids": ["fresh-b-proof"],
            },
        ],
        "fixture_dependency_scan": {
            "status": "PASS",
            "scanner_id": "fixture-scan-1",
            "scanned_paths": ["src/product.py"],
            "findings": [],
            "evidence_ids": ["fixture-scan-proof"],
        },
        "reference_regression": {"status": "PASS", "evidence_ids": ["reference-proof"]},
        "continuity_results": {"save_reopen": "PASS", "downstream_continuity": "PASS"},
        "security_results": {"cross_run_isolation": "PASS"},
        "full_regression": {"status": "PASS", "evidence_ids": ["full-regression-proof"]},
    }
    value.update(overrides)
    return value


class GeneralizationGateTests(unittest.TestCase):
    def test_generalized_fresh_inputs_pass(self):
        c = contract()
        result = GeneralizationGate().evaluate(c, evidence(c))
        self.assertEqual("PASS", result.status)
        self.assertTrue(result.authoritative)
        self.assertEqual(("fresh-a", "fresh-b"), result.scenario_ids)

    def test_reference_only_acceptance_fails_closed(self):
        c = contract()
        e = evidence(c)
        e["generalized_scenarios"] = [{
            "scenario_id": "reference-case",
            "input_identity": "reference-input",
            "materially_different": False,
            "reference_fixture": True,
            "runtime_path_identity": "generic-runtime-v1",
            "boundary_results": {name: "PASS" for name in c["required_full_path_boundaries"]},
            "evidence_ids": ["reference-proof"],
        }]
        result = GeneralizationGate().evaluate(c, e)
        self.assertEqual("HOLD", result.status)
        self.assertIn(FIXTURE_TARGET_COLLAPSE, result.escape_classes)

    def test_missing_whole_system_audit_fails_closed(self):
        c = contract()
        result = GeneralizationGate().evaluate(c, evidence(c, system_map_status="MISSING"))
        self.assertEqual("HOLD", result.status)
        self.assertIn(SEQUENTIAL_BLOCKER_TUNNELING, result.escape_classes)

    def test_changed_acceptance_boundary_fails_closed(self):
        c = contract()
        result = GeneralizationGate().evaluate(c, evidence(c, contract_digest="0" * 40))
        self.assertEqual("HOLD", result.status)
        self.assertIn(SEQUENTIAL_BLOCKER_TUNNELING, result.escape_classes)

    def test_fixture_dependency_scanner_detects_runtime_leakage(self):
        scan = scan_runtime_fixture_dependencies(
            {"src/product.py": "if fixture_id == 'known-reference':\n    return 91\n"},
            reference_tokens=("known-reference",),
        )
        self.assertEqual("FAIL", scan["status"])
        self.assertTrue(scan["findings"])

    def test_fixture_specific_mode_requires_governed_authorization(self):
        c = contract(
            mode="FIXTURE_SPECIFIC_AUTHORIZED",
            fixture_specific_authorization={
                "authorized_by": "HUMAN",
                "reason": "The product capability is intentionally scoped to one immutable reference artifact.",
                "evidence_id": "human-auth-1",
            },
        )
        result = GeneralizationGate().evaluate(c, {
            "issuer_role": "INDEPENDENT_VERIFIER",
            "authoritative": True,
            "contract_digest": GeneralizationGate().contract_digest(c),
            "acceptance_boundary_unchanged": True,
            "system_map_status": "PASS",
            "whole_authorized_scope_closed": True,
            "closure_definition_of_done_met": True,
            "reference_regression": {"status": "PASS", "evidence_ids": ["reference-proof"]},
        })
        self.assertEqual("AUTHORIZED_FIXTURE_SPECIFIC", result.status)
        self.assertTrue(result.fixture_specific_authorized)


if __name__ == "__main__":
    unittest.main()
