import json
import unittest

from gacm.provider_authority import ExternalProviderAuthorityGate


class ExternalProviderAuthorityGateTests(unittest.TestCase):
    def setUp(self):
        self.gate = ExternalProviderAuthorityGate()

    def authority(self, **overrides):
        value = {
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
            "candidate_release_sha": "abc123",
            "authorization_scope": "semantic-evaluation",
            "provider_authority": "AUTHORIZED",
        }
        value.update(overrides)
        return value

    def request(self, **overrides):
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

    def reasons(self, authority=None, request=None):
        return set(self.gate.evaluate(
            self.authority() if authority is None else authority,
            self.request() if request is None else request,
        ).reasons)

    def test_unknown_provider_fails(self):
        authority = self.authority(provider_authority="DISCOVERED")
        self.assertIn("PROVIDER_AUTHORITY_UNPROVEN", self.reasons(authority=authority))

    def test_available_but_unauthorized_credential_fails(self):
        authority = self.authority(credential_provenance="AVAILABLE_BUT_UNAUTHORIZED")
        self.assertIn("CREDENTIAL_PROVENANCE_UNPROVEN", self.reasons(authority=authority))

    def test_wrong_credential_provenance_fails(self):
        request = self.request(credential_source_id="global/provider-a-token")
        self.assertIn("CREDENTIAL_PROVENANCE_UNPROVEN", self.reasons(request=request))

    def test_wrong_endpoint_fails(self):
        request = self.request(endpoint_identity="https://proxy.example/v1")
        self.assertIn("ENDPOINT_IDENTITY_MISMATCH", self.reasons(request=request))

    def test_wrong_model_variant_fails(self):
        request = self.request(model_api_variant="model-a-cheaper")
        self.assertIn("MODEL_IDENTITY_MISMATCH", self.reasons(request=request))

    def test_multiple_discovered_credentials_do_not_authorize_selection(self):
        authority = self.authority()
        authority.pop("credential_source_id")
        request = self.request(discovered_credentials=["global-a", "global-b"])
        self.assertIn("CREDENTIAL_PROVENANCE_UNPROVEN", self.reasons(authority=authority, request=request))

    def test_api_compatible_substitute_fails(self):
        request = self.request(
            provider_id="provider-b",
            endpoint_identity="https://compatible.provider-b.example/v1",
            api_compatible_substitute=True,
        )
        reasons = self.reasons(request=request)
        self.assertIn("PROVIDER_IDENTITY_MISMATCH", reasons)
        self.assertIn("UNAUTHORIZED_PROVIDER_SUBSTITUTION", reasons)

    def test_matching_manifest_runtime_does_not_override_missing_authority(self):
        authority = self.authority(provider_authority="DISCOVERED")
        result = self.gate.evaluate(authority, self.request())
        self.assertEqual("HOLD", result.status)
        self.assertIn("PROVIDER_AUTHORITY_UNPROVEN", result.reasons)

    def test_spend_authorization_does_not_override_provider_authority(self):
        authority = self.authority(provider_authority="DISCOVERED", paid_calls_authorized=True)
        self.assertIn("PROVIDER_AUTHORITY_UNPROVEN", self.reasons(authority=authority))

    def test_explicitly_authorized_provider_proceeds(self):
        result = self.gate.evaluate(self.authority(), self.request())
        self.assertEqual("PASS", result.status)
        self.assertTrue(result.authoritative)

    def test_secret_values_are_rejected_from_identity_record(self):
        authority = self.authority(api_key="sk-secret-value")
        result = self.gate.evaluate(authority, self.request())
        self.assertEqual("HOLD", result.status)
        self.assertIn("SECRET_MATERIAL_PRESENT_IN_PROVIDER_IDENTITY_RECORD", result.reasons)
        self.assertNotIn("sk-secret-value", json.dumps(result.to_dict()))

    def test_authority_survives_handoff_restart(self):
        first = self.gate.evaluate(self.authority(), self.request())
        restored_authority = json.loads(json.dumps(self.authority()))
        restored_request = json.loads(json.dumps(self.request()))
        second = self.gate.evaluate(restored_authority, restored_request)
        self.assertEqual("PASS", second.status)
        self.assertEqual(first.identity_digest, second.identity_digest)


if __name__ == "__main__":
    unittest.main()
