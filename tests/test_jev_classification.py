import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gacm.classification import (  # noqa: E402
    GACM_INPUT_KIND_QUESTION,
    GACM_INPUT_KIND_TITLES,
    JevClassificationError,
    JevClient,
    JevGraphIntake,
    deterministic_title,
    graph_node_type,
)
from gacm.graph import (  # noqa: E402
    ActionKind,
    EpistemicState,
    GovernedGraph,
    GraphScheduler,
    NodeType,
    ProducerRole,
)
from gacm.provider_authority import ExternalProviderAuthorityGate  # noqa: E402


def authorized_provider_gate(
    *,
    endpoint="https://api.typesafe.ai/v1/systemone",
    model="jev-latest",
):
    authority = {
        "provider_id": "typesafe-ai",
        "account_identity": "gacm-prototype-typesafe",
        "environment": "development",
        "endpoint_identity": endpoint,
        "model_api_variant": model,
        "credential_source_id": "windows-user:JEV_API_KEY",
        "credential_provenance": "VERIFIED",
        "governing_authority_artifact": "test://explicit-typesafe-authorization",
        "authorization_scope": "GACM_PROTOTYPE_CLASSIFICATION",
        "provider_authority": "AUTHORIZED",
        "model_variant_required": True,
    }
    request = {
        "provider_id": "typesafe-ai",
        "account_identity": "gacm-prototype-typesafe",
        "environment": "development",
        "endpoint_identity": endpoint,
        "model_api_variant": model,
        "credential_source_id": "windows-user:JEV_API_KEY",
    }
    result = ExternalProviderAuthorityGate().evaluate(authority, request)
    assert result.status == "PASS"
    return result


def fake_transport(endpoint, headers, payload):
    return {
        "model": "jev-latest",
        "answers": {
            "input_kind": {
                "type": "choice",
                "choice": "DEFECT",
                "confidence": 0.91,
                "probabilities": {
                    "DEFECT": 0.91,
                    "EVIDENCE_GAP": 0.03,
                    "REQUIREMENT": 0.02,
                    "CONSTRAINT": 0.01,
                    "DEPENDENCY": 0.01,
                    "RISK": 0.01,
                    "UNKNOWN": 0.01,
                },
            }
        },
        "usage": {"input_tokens": 37, "output_tokens": 8},
    }


class JevClassificationTests(unittest.TestCase):
    def test_default_model_and_fixed_taxonomy_are_sent(self):
        seen = {}

        def transport(endpoint, headers, payload):
            seen.update(
                {
                    "endpoint": endpoint,
                    "headers": dict(headers),
                    "payload": payload,
                }
            )
            return fake_transport(endpoint, headers, payload)

        result = JevClient(provider_gate_result=authorized_provider_gate(), transport=transport).classify(
            state={"symptom": "login button does nothing"},
            questions={"input_kind": GACM_INPUT_KIND_QUESTION},
        )
        self.assertEqual("jev-latest", seen["payload"]["model"])
        self.assertEqual(
            set(GACM_INPUT_KIND_TITLES),
            set(seen["payload"]["questions"]["input_kind"]["criteria"]),
        )
        self.assertEqual("jev-latest", result.resolved_model)
        self.assertEqual(37, result.input_tokens)
        self.assertFalse(result.to_dict()["authoritative"])

    def test_choice_projects_to_inferred_graph_node_with_code_owned_title(self):
        result = JevClient(provider_gate_result=authorized_provider_gate(), transport=fake_transport).classify(
            state="login button does nothing",
            questions={"input_kind": GACM_INPUT_KIND_QUESTION},
        )
        node = result.propose_graph_node(
            question_name="input_kind",
            taxonomy_titles=GACM_INPUT_KIND_TITLES,
            object_id="classified-defect-1",
            project_id="project-gacm",
            object_type=graph_node_type("DEFECT"),
            created_at="2026-10-03T21:10:00Z",
            source_snapshot_id="source-1",
            run_id="run-1",
        )
        self.assertEqual(NodeType.DEFECT, node.object_type)
        self.assertEqual(EpistemicState.INFERRED, node.epistemic_state)
        self.assertEqual(ProducerRole.ORCHESTRATION, node.producer_role)
        self.assertEqual("Defect", node.payload["title"])
        self.assertEqual("DEFECT", node.payload["classification_code"])
        self.assertIsNone(node.authority_ref)
        self.assertEqual("NOT_VERIFIED", node.verification_state)
        self.assertAlmostEqual(0.91, node.confidence)

    def test_jev_cannot_project_evidenced_or_accepted_truth(self):
        result = JevClient(provider_gate_result=authorized_provider_gate(), transport=fake_transport).classify(
            state="login button does nothing",
            questions={"input_kind": GACM_INPUT_KIND_QUESTION},
        )
        for state in (EpistemicState.EVIDENCED, EpistemicState.ACCEPTED):
            with self.assertRaises(JevClassificationError):
                result.propose_graph_node(
                    question_name="input_kind",
                    taxonomy_titles=GACM_INPUT_KIND_TITLES,
                    object_id="classified-1",
                    project_id="project-gacm",
                    object_type=NodeType.DEFECT,
                    created_at="2026-10-03T21:10:00Z",
                    source_snapshot_id="source-1",
                    epistemic_state=state,
                )

    def test_out_of_taxonomy_choice_is_rejected_at_provider_boundary(self):
        def transport(endpoint, headers, payload):
            response = fake_transport(endpoint, headers, payload)
            response["answers"]["input_kind"]["choice"] = "NOT_IN_TAXONOMY"
            return response

        with self.assertRaises(JevClassificationError):
            JevClient(provider_gate_result=authorized_provider_gate(), transport=transport).classify(
                state="something",
                questions={"input_kind": GACM_INPUT_KIND_QUESTION},
            )

    def test_invalid_choice_probability_is_rejected(self):
        def transport(endpoint, headers, payload):
            response = fake_transport(endpoint, headers, payload)
            response["answers"]["input_kind"]["probabilities"]["DEFECT"] = 1.2
            return response

        with self.assertRaises(JevClassificationError):
            JevClient(provider_gate_result=authorized_provider_gate(), transport=transport).classify(
                state="something",
                questions={"input_kind": GACM_INPUT_KIND_QUESTION},
            )

    def test_choice_probabilities_must_sum_to_approximately_one(self):
        def transport(endpoint, headers, payload):
            response = fake_transport(endpoint, headers, payload)
            response["answers"]["input_kind"]["probabilities"] = {
                key: 0.01
                for key in response["answers"]["input_kind"]["probabilities"]
            }
            return response

        with self.assertRaises(JevClassificationError):
            JevClient(provider_gate_result=authorized_provider_gate(), transport=transport).classify(
                state="something",
                questions={"input_kind": GACM_INPUT_KIND_QUESTION},
            )

    def test_response_question_set_must_match_request(self):
        def transport(endpoint, headers, payload):
            response = fake_transport(endpoint, headers, payload)
            response["answers"] = {"other": response["answers"]["input_kind"]}
            return response

        with self.assertRaises(JevClassificationError):
            JevClient(provider_gate_result=authorized_provider_gate(), transport=transport).classify(
                state="something",
                questions={"input_kind": GACM_INPUT_KIND_QUESTION},
            )

    def test_response_answer_type_must_match_question(self):
        def transport(endpoint, headers, payload):
            response = fake_transport(endpoint, headers, payload)
            response["answers"]["input_kind"]["type"] = "noul"
            return response

        with self.assertRaises(JevClassificationError):
            JevClient(provider_gate_result=authorized_provider_gate(), transport=transport).classify(
                state="something",
                questions={"input_kind": GACM_INPUT_KIND_QUESTION},
            )

    def test_claimed_provider_pass_dictionary_is_not_trusted(self):
        with self.assertRaises(ValueError):
            JevClient(
                provider_gate_result=authorized_provider_gate().to_dict(),
                transport=fake_transport,
            )

    def test_missing_provider_authority_blocks_even_with_transport(self):
        with self.assertRaises(JevClassificationError):
            JevClient(transport=fake_transport).classify(
                state="something",
                questions={"input_kind": GACM_INPUT_KIND_QUESTION},
            )

    def test_provider_authority_must_match_exact_endpoint(self):
        wrong_gate = authorized_provider_gate(
            endpoint="https://api.typesafe.ai/v1/other"
        )
        with self.assertRaises(JevClassificationError):
            JevClient(
                provider_gate_result=wrong_gate,
                transport=fake_transport,
            ).classify(
                state="something",
                questions={"input_kind": GACM_INPUT_KIND_QUESTION},
            )

    def test_provider_authority_must_match_exact_model_alias(self):
        wrong_gate = authorized_provider_gate(model="jev-preview")
        with self.assertRaises(JevClassificationError):
            JevClient(
                provider_gate_result=wrong_gate,
                transport=fake_transport,
            ).classify(
                state="something",
                questions={"input_kind": GACM_INPUT_KIND_QUESTION},
            )

    def test_missing_api_key_fails_before_network_transport(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(JevClassificationError):
                JevClient(provider_gate_result=authorized_provider_gate()).classify(
                    state="something",
                    questions={"input_kind": GACM_INPUT_KIND_QUESTION},
                )

    def test_jev_intake_records_inferred_candidate_and_scheduler_requests_evidence(self):
        graph = GovernedGraph()
        receipt = JevGraphIntake(
            JevClient(provider_gate_result=authorized_provider_gate(), transport=fake_transport)
        ).classify_and_record(
            graph,
            state={"symptom": "login button does nothing"},
            project_id="project-gacm",
            source_snapshot_id="source-1",
            created_at="2026-10-03T21:10:00Z",
            run_id="run-1",
        )
        node = graph.node(receipt.object_id)
        self.assertIsNotNone(node)
        self.assertEqual(EpistemicState.INFERRED, node.epistemic_state)
        self.assertFalse(receipt.to_dict()["authoritative"])
        actions = GraphScheduler(graph).next_actions("project-gacm", run_id="run-1")
        self.assertEqual(1, len(actions))
        self.assertEqual(ActionKind.COLLECT_EVIDENCE, actions[0].kind)
        self.assertEqual(receipt.object_id, actions[0].target_object_id)

    def test_titles_are_owned_by_deterministic_taxonomy(self):
        self.assertEqual("Evidence Gap", deterministic_title("EVIDENCE_GAP"))
        self.assertEqual(NodeType.EVIDENCE_GAP, graph_node_type("EVIDENCE_GAP"))
        with self.assertRaises(ValueError):
            deterministic_title("INVENTED")


if __name__ == "__main__":
    unittest.main()
