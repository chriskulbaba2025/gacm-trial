import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gacm.generalization import GATE_ID, GeneralizationGate  # noqa: E402
from gacm.promotion.eligibility import PromotionEligibility  # noqa: E402
from gacm.provider_authority import ExternalProviderAuthorityGate  # noqa: E402


def generalization_pair():
    contract = {
        "gate_id": GATE_ID,
        "mode": "GENERALIZED",
        "product_definition_of_done": "Variable valid inputs traverse the capability end-to-end.",
        "authorized_capability_scope": ["capability"],
        "connected_system_path": ["input", "processing", "output"],
        "required_full_path_boundaries": ["input", "processing", "output"],
        "minimum_fresh_scenarios": 2,
        "reference_regression_ids": ["reference-case"],
    }
    digest = GeneralizationGate().contract_digest(contract)
    evidence = {
        "issuer_role": "INDEPENDENT_VERIFIER",
        "authoritative": True,
        "contract_digest": digest,
        "acceptance_boundary_unchanged": True,
        "system_map_status": "PASS",
        "whole_authorized_scope_closed": True,
        "closure_definition_of_done_met": True,
        "generalized_scenarios": [
            {
                "scenario_id": "fresh-a", "input_identity": "a", "materially_different": True,
                "reference_fixture": False, "runtime_path_identity": "generic",
                "boundary_results": {"input": "PASS", "processing": "PASS", "output": "PASS"},
                "evidence_ids": ["fresh-a"],
            },
            {
                "scenario_id": "fresh-b", "input_identity": "b", "materially_different": True,
                "reference_fixture": False, "runtime_path_identity": "generic",
                "boundary_results": {"input": "PASS", "processing": "PASS", "output": "PASS"},
                "evidence_ids": ["fresh-b"],
            },
        ],
        "fixture_dependency_scan": {
            "status": "PASS", "scanner_id": "scan", "scanned_paths": ["src/product.py"],
            "findings": [], "evidence_ids": ["scan"],
        },
        "reference_regression": {"status": "PASS", "evidence_ids": ["reference"]},
        "full_regression": {"status": "PASS", "evidence_ids": ["full"]},
    }
    return contract, evidence


def provider_authority():
    return {
        "gate_id": "GACM-EXTERNAL-PROVIDER-AUTHORITY-AND-CREDENTIAL-PROVENANCE-GATE",
        "provider_id": "provider-a",
        "service_id": "service-a",
        "account_identity": "acct-project-a",
        "environment": "staging",
        "endpoint_identity": "https://api.provider-a.example/v1",
        "model_api_variant": "model-a-v1",
        "model_variant_required": True,
        "credential_source_id": "project-secret/provider-a/staging",
        "credential_provenance": "VERIFIED",
        "governing_authority_artifact": "governance/provider-manifest-a",
        "authorization_scope": "semantic-evaluation",
        "provider_authority": "AUTHORIZED",
    }


def provider_request(**overrides):
    value = {
        "provider_id": "provider-a",
        "account_identity": "acct-project-a",
        "environment": "staging",
        "endpoint_identity": "https://api.provider-a.example/v1",
        "model_api_variant": "model-a-v1",
        "credential_source_id": "project-secret/provider-a/staging",
    }
    value.update(overrides)
    return value


def promotion_evidence(**overrides):
    contract, generalized = generalization_pair()
    auth = provider_authority()
    request = provider_request()
    gate = ExternalProviderAuthorityGate().evaluate(auth, request).to_dict()
    value = {
        "github_authority_status": "VERIFIED",
        "operational_context_status": "VERIFIED",
        "execution_status": "COMPLETED",
        "identity_validation_result": "VALID",
        "verification": {"status": "PASS", "authoritative": True, "issuer_role": "INDEPENDENT_VERIFIER"},
        "rollback_target_sha": "c" * 40,
        "candidate_sha": "b" * 40,
        "candidate_artifact_identity": "artifact-b",
        "candidate_identity_matches": True,
        "authority_continuity": True,
        "generalization_contract": contract,
        "generalization_evidence": generalized,
        "external_action_required": True,
        "external_provider_authority": auth,
        "external_provider_request": request,
        "external_provider_gate": gate,
    }
    value.update(overrides)
    return value


class ProviderPromotionAndSchemaTests(unittest.TestCase):
    def test_promotion_blocks_unproven_provider(self):
        auth = provider_authority()
        auth["provider_authority"] = "DISCOVERED"
        result = PromotionEligibility().evaluate(
            promotion_evidence(external_provider_authority=auth)
        )
        self.assertFalse(result.eligible)
        self.assertIn("EXTERNAL_PROVIDER_AUTHORITY_GATE_NOT_SATISFIED", result.reasons)

    def test_promotion_blocks_claimed_gate_mismatch(self):
        claimed = promotion_evidence()["external_provider_gate"]
        claimed["identity_digest"] = "wrong"
        result = PromotionEligibility().evaluate(
            promotion_evidence(external_provider_gate=claimed)
        )
        self.assertFalse(result.eligible)
        self.assertIn("EXTERNAL_PROVIDER_GATE_CLAIM_MISMATCH", result.reasons)

    def test_promotion_accepts_explicit_provider_authority(self):
        result = PromotionEligibility().evaluate(promotion_evidence())
        self.assertTrue(result.eligible)

    def test_schema_release_1_2_requires_provider_gate_for_external_action(self):
        schema = json.loads((ROOT / "schemas/gacm-run-state.schema.json").read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        state = json.loads((ROOT / "tests/fixtures/valid_new_run.json").read_text(encoding="utf-8"))
        state["gacm"]["schema_release"] = "1.2.0"
        state["external_action_required"] = True
        contract, generalized = generalization_pair()
        state["generalization_contract"] = contract
        state["generalization_gate"] = GeneralizationGate().evaluate(contract, generalized).to_dict()
        errors = list(validator.iter_errors(state))
        self.assertTrue(errors)

        auth = provider_authority()
        request = provider_request()
        gate = ExternalProviderAuthorityGate().evaluate(auth, request).to_dict()
        state["external_provider_authority"] = auth
        state["external_provider_gate"] = gate
        errors = list(validator.iter_errors(state))
        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
