import unittest

from gacm.harness.pilot import HarnessAdapters, HarnessConfig, PilotHarness


class ProviderAuthorityHarnessTests(unittest.TestCase):
    def test_unauthorized_external_action_blocks_before_route_or_execute(self):
        calls = {"route": 0, "execute": 0}

        def route(unit):
            calls["route"] += 1
            return {
                "status": "QUALIFIED",
                "qualification_identity": "q1",
                "selected_model": "model-a-v1",
            }

        def execute(unit, selected_route, context):
            calls["execute"] += 1
            return {"execution_status": "COMPLETED"}

        adapters = HarnessAdapters(
            authority=lambda config: {"status": "VERIFIED"},
            discovery=lambda config, authority: {},
            context=lambda config, authority, discovery: {"status": "VERIFIED"},
            plan=lambda config, context, units: [{
                "id": "external-unit",
                "external_action_required": True,
                "external_provider_request": {
                    "provider_id": "provider-a",
                    "account_identity": "acct-project-a",
                    "environment": "staging",
                    "endpoint_identity": "https://api.provider-a.example/v1",
                    "model_api_variant": "model-a-v1",
                    "credential_source_id": "global-token",
                },
            }],
            route=route,
            execute=execute,
            verify=lambda unit, execution, context: {
                "status": "PASS", "authoritative": True, "issuer_role": "INDEPENDENT_VERIFIER"
            },
        )
        config = HarnessConfig(
            project_id="project-a",
            prd_identity="prd-a",
            authoritative_start_sha="sha-a",
            branch_or_worktree="branch-a",
            gacm_version="test",
            execution_policy={},
            human_authority={},
            discovery_config={},
            operational_context_requirements={},
            settle_required=False,
            generalization_contract={
                "gate_id": "GACM-GENERALIZATION-AND-WHOLE-SYSTEM-GATE",
                "mode": "GENERALIZED",
                "product_definition_of_done": "generic",
                "authorized_capability_scope": ["external action"],
                "connected_system_path": ["input", "execution"],
                "required_full_path_boundaries": ["execution"],
                "minimum_fresh_scenarios": 2,
            },
            external_provider_authority={
                "provider_id": "provider-a",
                "service_id": "service-a",
                "account_identity": "acct-project-a",
                "environment": "staging",
                "endpoint_identity": "https://api.provider-a.example/v1",
                "model_api_variant": "model-a-v1",
                "model_variant_required": True,
                "credential_source_id": "project-secret/provider-a/staging",
                "credential_provenance": "VERIFIED",
                "governing_authority_artifact": "provider-manifest-a",
                "authorization_scope": "external action",
                "provider_authority": "AUTHORIZED",
            },
        )

        state = PilotHarness(adapters).run(config)

        self.assertEqual("BLOCKED", state["state"])
        self.assertTrue(any("EXTERNAL_PROVIDER_AUTHORITY_GATE_HOLD" in x for x in state["blockers"]))
        self.assertEqual(0, calls["route"])
        self.assertEqual(0, calls["execute"])


    def test_required_policy_rejects_missing_external_action_classification(self):
        calls = {"route": 0, "execute": 0}

        def route(unit):
            calls["route"] += 1
            return {"status": "QUALIFIED", "qualification_identity": "q1", "selected_model": "local"}

        def execute(unit, selected_route, context):
            calls["execute"] += 1
            return {"execution_status": "COMPLETED"}

        adapters = HarnessAdapters(
            authority=lambda config: {"status": "VERIFIED"},
            discovery=lambda config, authority: {},
            context=lambda config, authority, discovery: {"status": "VERIFIED"},
            plan=lambda config, context, units: [{"id": "unclassified"}],
            route=route,
            execute=execute,
            verify=lambda unit, execution, context: {
                "status": "PASS", "authoritative": True, "issuer_role": "INDEPENDENT_VERIFIER"
            },
        )
        config = HarnessConfig(
            project_id="project-a",
            prd_identity="prd-a",
            authoritative_start_sha="sha-a",
            branch_or_worktree="branch-a",
            gacm_version="test",
            execution_policy={"external_provider_authority_gate": "REQUIRED"},
            human_authority={},
            discovery_config={},
            operational_context_requirements={},
            settle_required=False,
            generalization_contract={
                "gate_id": "GACM-GENERALIZATION-AND-WHOLE-SYSTEM-GATE",
                "mode": "GENERALIZED",
                "product_definition_of_done": "generic",
                "authorized_capability_scope": ["work"],
                "connected_system_path": ["input", "execution"],
                "required_full_path_boundaries": ["execution"],
                "minimum_fresh_scenarios": 2,
            },
        )
        state = PilotHarness(adapters).run(config)
        self.assertEqual("BLOCKED", state["state"])
        self.assertIn("EXTERNAL_ACTION_CLASSIFICATION_REQUIRED", state["blockers"])
        self.assertEqual(0, calls["route"])
        self.assertEqual(0, calls["execute"])

    def test_required_policy_rejects_undeclared_provider_route_before_execute(self):
        calls = {"execute": 0}

        def execute(unit, selected_route, context):
            calls["execute"] += 1
            return {"execution_status": "COMPLETED"}

        adapters = HarnessAdapters(
            authority=lambda config: {"status": "VERIFIED"},
            discovery=lambda config, authority: {},
            context=lambda config, authority, discovery: {"status": "VERIFIED"},
            plan=lambda config, context, units: [{"id": "declared-non-external", "external_action_required": False}],
            route=lambda unit: {
                "status": "QUALIFIED",
                "qualification_identity": "q1",
                "selected_model": "model-a",
                "selected_provider": "provider-a",
            },
            execute=execute,
            verify=lambda unit, execution, context: {
                "status": "PASS", "authoritative": True, "issuer_role": "INDEPENDENT_VERIFIER"
            },
        )
        config = HarnessConfig(
            project_id="project-a",
            prd_identity="prd-a",
            authoritative_start_sha="sha-a",
            branch_or_worktree="branch-a",
            gacm_version="test",
            execution_policy={"external_provider_authority_gate": "REQUIRED"},
            human_authority={},
            discovery_config={},
            operational_context_requirements={},
            settle_required=False,
            generalization_contract={
                "gate_id": "GACM-GENERALIZATION-AND-WHOLE-SYSTEM-GATE",
                "mode": "GENERALIZED",
                "product_definition_of_done": "generic",
                "authorized_capability_scope": ["work"],
                "connected_system_path": ["input", "execution"],
                "required_full_path_boundaries": ["execution"],
                "minimum_fresh_scenarios": 2,
            },
        )
        state = PilotHarness(adapters).run(config)
        self.assertEqual("BLOCKED", state["state"])
        self.assertIn("UNDECLARED_EXTERNAL_PROVIDER_ROUTE", state["blockers"])
        self.assertEqual(0, calls["execute"])


if __name__ == "__main__":
    unittest.main()
