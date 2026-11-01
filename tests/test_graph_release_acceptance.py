from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gacm.generalization import GATE_ID, GeneralizationGate  # noqa: E402
from gacm.promotion import PromotionEligibility, PromotionRollbackStateMachine  # noqa: E402
from gacm.verification import IndependentVerificationEngine, VerificationInput, evidence_digest  # noqa: E402


START = "a" * 40
CANDIDATE = "b" * 40
ROLLBACK = "c" * 40
ARTIFACT = "d" * 64
GRAPH_PROJECTION = "e" * 64
SOURCE_EVENT = "f" * 64
ENGINE = "1" * 40
ENGINE_MANIFEST = "2" * 64
ENVIRONMENT = "staging-env-1"
_DEFAULT_EVIDENCE = object()


def graph_contract(**overrides):
    value = {
        "schema": "GACM_GRAPH_RELEASE_CONTRACT_V1",
        "project_id": "project-release",
        "candidate_sha": CANDIDATE,
        "candidate_artifact_identity": ARTIFACT,
        "environment_id": ENVIRONMENT,
        "graph_schema": "GACM_GRAPH_RUNTIME_STATUS_V1",
        "graph_engine_authority_sha": ENGINE,
        "graph_engine_manifest_sha256": ENGINE_MANIFEST,
        "retrieval_materially_used": True,
        "convergence_materially_used": True,
    }
    value.update(overrides)
    return value


def graph_evidence(**overrides):
    value = {
        "schema": "GACM_GRAPH_RELEASE_EVIDENCE_V1",
        "project_id": "project-release",
        "candidate_sha": CANDIDATE,
        "candidate_artifact_identity": ARTIFACT,
        "remote_candidate_sha": CANDIDATE,
        "deployed_artifact_sha": CANDIDATE,
        "served_runtime_sha": CANDIDATE,
        "environment_id": ENVIRONMENT,
        "build_identity": "deployment-1",
        "source_identities": [
            {"source_id": "runtime-source-tree", "identity_digest": ARTIFACT},
            {"source_id": "graph-source-event", "identity_digest": SOURCE_EVENT},
        ],
        "graph": {
            "schema": "GACM_GRAPH_RUNTIME_STATUS_V1",
            "status": "PASS",
            "graph_revision": 7,
            "projection_digest": GRAPH_PROJECTION,
            "source_event_hash": SOURCE_EVENT,
            "engine_authority_sha": ENGINE,
            "engine_manifest_sha256": ENGINE_MANIFEST,
        },
        "retrieval": {
            "materially_used": True,
            "status": "AVAILABLE",
            "mechanism": "DETERMINISTIC_LEXICAL_V1+GOVERNED_GRAPH_DEPTH_1",
            "index_identity": "gacm-lexical-v1",
            "receipt_digest": "3" * 64,
            "graph_revision": 7,
            "projection_digest": GRAPH_PROJECTION,
            "corpus_snapshot_digest": "4" * 64,
            "query_digest": "5" * 64,
            "returned_object_ids": ["requirement:r1"],
        },
        "convergence": {
            "materially_used": True,
            "status": "PASS",
            "detector_identity": "gacm-deterministic-convergence-v1",
            "result_digest": "6" * 64,
            "graph_revision": 7,
            "projection_digest": GRAPH_PROJECTION,
            "source_event_hash": SOURCE_EVENT,
            "candidate_count": 2,
            "epistemic_limit": "POSSIBLE_SHARED_ROOT_CAUSE",
            "authority": "ADVISORY_DIAGNOSTIC_ONLY",
            "authoritative_root_cause_established": False,
            "lexical_similarity_used": False,
            "vector_similarity_used": False,
            "model_judgment_used": False,
        },
        "assertions": [
            {
                "assertion_id": "assert-current-release",
                "kind": "RELEASE_CURRENTNESS",
                "object_ids": ["release:candidate"],
                "evidence_ids": ["ev-runtime", "ev-deployment", "ev-graph"],
                "provenance_refs": ["git:candidate", "railway:deployment", "api:graph"],
                "graph_revision": 7,
                "projection_digest": GRAPH_PROJECTION,
                "epistemic_state": "EVIDENCED",
                "verification_state": "VERIFIED",
                "release_gate_role": "SATISFIES_RELEASE_GATE",
            },
            {
                "assertion_id": "assert-convergence-context",
                "kind": "CONVERGENCE_CONTEXT",
                "object_ids": ["conv:1"],
                "evidence_ids": ["ev-convergence"],
                "provenance_refs": ["api:convergence"],
                "graph_revision": 7,
                "projection_digest": GRAPH_PROJECTION,
                "epistemic_state": "POSSIBLE_SHARED_ROOT_CAUSE",
                "verification_state": "VERIFIED",
                "release_gate_role": "CONTEXT_ONLY",
            },
        ],
    }
    value.update(overrides)
    return value


def verification_input(*, graph_required=True, evidence=_DEFAULT_EVIDENCE, contract_overrides=None):
    contract = {
        "run_id": "run-release",
        "work_unit_id": "unit-release",
        "authorized_start_sha": START,
        "repository_id": "repo-release",
        "branch": "candidate/release",
        "worktree": "C:/work/release",
        "context_snapshot_id": "ctx-release",
        "context_snapshot_revision": "1",
        "selected_model": "NO_EXTERNAL_EXECUTOR_MODEL",
        "qualification_identity": "direct-governed-edit-no-executor-model",
        "routing_decision_id": "route-release",
        "graph_release_required": graph_required,
    }
    if graph_required:
        contract["graph_release_contract"] = graph_contract(**(contract_overrides or {}))
    receipt = {
        "run_id": "run-release",
        "work_unit_id": "unit-release",
        "execution_id": "exec-release",
        "starting_sha": START,
        "ending_sha": CANDIDATE,
        "model_used": "NO_EXTERNAL_EXECUTOR_MODEL",
        "qualification_identity": "direct-governed-edit-no-executor-model",
        "files_changed": ["src/release.py"],
        "execution_status": "COMPLETED",
        "authoritative_pass": False,
    }
    return VerificationInput(
        run_state={"run_id": "run-release"},
        work_unit_contract=contract,
        execution_receipt=receipt,
        starting_repository={"sha": START, "repository_id": "repo-release", "branch": "candidate/release", "worktree": "C:/work/release"},
        ending_repository={"sha": CANDIDATE, "repository_id": "repo-release", "branch": "candidate/release", "worktree": "C:/work/release"},
        actual_changed_paths=("src/release.py",),
        diff_evidence={"source": "git", "base": START, "head": CANDIDATE},
        test_contract=("release-currentness",),
        test_outcomes={"release-currentness": {"status": "PASS", "runner": "unittest", "result_digest": "c" * 64, "candidate_sha": CANDIDATE}},
        allowed_writable_surfaces=("src/*",),
        forbidden_surfaces=("production/*",),
        operational_context={"status": "VERIFIED", "context_id": "ctx-release", "context_revision": "1"},
        routing_decision={"decision_id": "route-release", "selected_model": "NO_EXTERNAL_EXECUTOR_MODEL", "qualification_identity": "direct-governed-edit-no-executor-model"},
        broader_requalification_triggers=("SHARED_AUTHORITY", "ARCHITECTURE"),
        claimed_affected_scope=("src/release.py",),
        scope_patterns={"authority": ("CURRENT_STATE.md",), "architecture": ("schemas/*",)},
        expected_outcome_met=True,
        graph_release_evidence=(graph_evidence() if evidence is _DEFAULT_EVIDENCE and graph_required else (None if evidence is _DEFAULT_EVIDENCE else evidence)),
    )


def generalization_pair():
    contract = {
        "gate_id": GATE_ID,
        "mode": "GENERALIZED",
        "product_definition_of_done": "Release evidence is independently verifiable.",
        "authorized_capability_scope": ["release"],
        "connected_system_path": ["evidence", "verification", "promotion"],
        "required_full_path_boundaries": ["evidence", "verification", "promotion"],
        "minimum_fresh_scenarios": 2,
        "reference_regression_ids": ["reference-release"],
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
            {"scenario_id": "fresh-a", "input_identity": "a", "materially_different": True, "reference_fixture": False, "runtime_path_identity": "generic", "boundary_results": {"evidence": "PASS", "verification": "PASS", "promotion": "PASS"}, "evidence_ids": ["fresh-a"]},
            {"scenario_id": "fresh-b", "input_identity": "b", "materially_different": True, "reference_fixture": False, "runtime_path_identity": "generic", "boundary_results": {"evidence": "PASS", "verification": "PASS", "promotion": "PASS"}, "evidence_ids": ["fresh-b"]},
        ],
        "fixture_dependency_scan": {"status": "PASS", "scanner_id": "scan", "scanned_paths": ["src/release.py"], "findings": [], "evidence_ids": ["scan"]},
        "reference_regression": {"status": "PASS", "evidence_ids": ["reference"]},
        "full_regression": {"status": "PASS", "evidence_ids": ["full"]},
    }
    return contract, evidence


def promotion_evidence(verification, digest, **overrides):
    generalization_contract, generalization_evidence = generalization_pair()
    value = {
        "run_id": "run-release",
        "github_authority_status": "VERIFIED",
        "operational_context_status": "VERIFIED",
        "execution_status": "COMPLETED",
        "identity_validation_result": "VALID",
        "verification": verification,
        "verification_receipt_ids": (verification["verification_id"],),
        "rollback_target_sha": ROLLBACK,
        "candidate_sha": CANDIDATE,
        "candidate_artifact_identity": ARTIFACT,
        "current_authoritative_sha": START,
        "candidate_identity_matches": True,
        "authority_continuity": True,
        "operational_context_id": "ctx-release",
        "generalization_contract": generalization_contract,
        "generalization_evidence": generalization_evidence,
        "graph_release_required": True,
        "graph_release_evidence_digest": digest,
    }
    value.update(overrides)
    return value


class GraphReleaseVerificationTests(unittest.TestCase):
    def setUp(self):
        self.engine = IndependentVerificationEngine(clock=lambda: "2026-10-04T16:00:00Z")

    def test_non_graph_verification_remains_backward_compatible(self):
        result = self.engine.verify(verification_input(graph_required=False, evidence=None))
        self.assertEqual("PASS", result.status)
        self.assertEqual("NOT_APPLICABLE", result.graph_release_result)
        self.assertIsNone(result.graph_release_evidence_digest)

    def test_graph_release_requires_raw_evidence(self):
        result = self.engine.verify(verification_input(evidence=None))
        self.assertEqual("UNOBSERVABLE", result.status)
        self.assertEqual("UNOBSERVABLE", result.graph_release_result)
        self.assertFalse(result.authoritative)

    def test_valid_graph_release_is_independently_verified_and_deterministic(self):
        evidence = graph_evidence()
        first = self.engine.verify(verification_input(evidence=evidence))
        second = self.engine.verify(verification_input(evidence=copy.deepcopy(evidence)))
        self.assertEqual("PASS", first.status)
        self.assertTrue(first.authoritative)
        self.assertEqual("PASS", first.graph_release_result)
        self.assertEqual(evidence_digest(evidence), first.graph_release_evidence_digest)
        self.assertIn("graph_release_evidence", first.evidence_reviewed)
        self.assertEqual(first.verification_id, second.verification_id)

    def test_release_currentness_identity_mismatch_fails(self):
        evidence = graph_evidence(served_runtime_sha="9" * 40)
        result = self.engine.verify(verification_input(evidence=evidence))
        self.assertEqual("FAIL", result.status)
        self.assertIn("release currentness identity mismatch", result.reasons)

    def test_stale_material_retrieval_fails(self):
        evidence = graph_evidence()
        evidence["retrieval"]["graph_revision"] = 6
        result = self.engine.verify(verification_input(evidence=evidence))
        self.assertEqual("FAIL", result.status)
        self.assertIn("material retrieval evidence is stale relative to release graph", result.reasons)

    def test_stale_convergence_fails(self):
        evidence = graph_evidence()
        evidence["convergence"]["projection_digest"] = "7" * 64
        result = self.engine.verify(verification_input(evidence=evidence))
        self.assertEqual("FAIL", result.status)
        self.assertIn("material convergence evidence is stale relative to release graph", result.reasons)

    def test_possible_shared_root_cannot_satisfy_release_gate(self):
        evidence = graph_evidence()
        evidence["assertions"][0]["epistemic_state"] = "POSSIBLE_SHARED_ROOT_CAUSE"
        result = self.engine.verify(verification_input(evidence=evidence))
        self.assertEqual("FAIL", result.status)
        self.assertTrue(any("epistemic state cannot satisfy release" in reason for reason in result.reasons))

    def test_evidenced_but_unverified_assertion_cannot_satisfy_release_gate(self):
        evidence = graph_evidence()
        evidence["assertions"][0]["verification_state"] = "NOT_VERIFIED"
        result = self.engine.verify(verification_input(evidence=evidence))
        self.assertEqual("FAIL", result.status)
        self.assertTrue(any("not independently VERIFIED" in reason for reason in result.reasons))

    def test_stale_assertion_fails(self):
        evidence = graph_evidence()
        evidence["assertions"][0]["graph_revision"] = 6
        result = self.engine.verify(verification_input(evidence=evidence))
        self.assertEqual("FAIL", result.status)
        self.assertTrue(any("is stale" in reason for reason in result.reasons))

    def test_context_only_convergence_remains_advisory(self):
        evidence = graph_evidence()
        result = self.engine.verify(verification_input(evidence=evidence))
        context_assertion = evidence["assertions"][1]
        self.assertEqual("POSSIBLE_SHARED_ROOT_CAUSE", context_assertion["epistemic_state"])
        self.assertEqual("CONTEXT_ONLY", context_assertion["release_gate_role"])
        self.assertEqual("PASS", result.graph_release_result)

    def test_receipt_projection_persists_graph_release_identity(self):
        result = self.engine.verify(verification_input(evidence=graph_evidence()))
        projection = result.to_run_state_projection()
        verification = projection["work_unit"]["verification"]
        self.assertEqual("PASS", verification["graph_release_result"])
        self.assertEqual(result.graph_release_evidence_digest, verification["graph_release_evidence_digest"])
        state = json.loads((ROOT / "tests/fixtures/valid_multi_unit_running.json").read_text(encoding="utf-8"))
        state["evidence"].append(projection["evidence"])
        state["work_units"][1].update({
            "status": projection["work_unit"]["status"],
            "verification": verification,
            "affected_scope": projection["work_unit"]["affected_scope"],
            "broader_requalification_triggers": [],
            "output_evidence": projection["work_unit"]["output_evidence"],
        })
        schema = json.loads((ROOT / "schemas/gacm-run-state.schema.json").read_text(encoding="utf-8"))
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(state))
        self.assertEqual([], errors)


class GraphReleasePromotionTests(unittest.TestCase):
    def setUp(self):
        self.engine = IndependentVerificationEngine(clock=lambda: "2026-10-04T16:00:00Z")

    def verified(self):
        return self.engine.verify(verification_input(evidence=graph_evidence())).to_dict()

    def test_generic_verifier_pass_is_insufficient_for_graph_backed_promotion(self):
        verifier = self.verified()
        verifier["graph_release_result"] = "NOT_APPLICABLE"
        result = PromotionEligibility().evaluate(
            promotion_evidence(verifier, evidence_digest(graph_evidence()))
        )
        self.assertFalse(result.eligible)
        self.assertIn("GRAPH_RELEASE_VERIFIER_PASS_REQUIRED", result.reasons)

    def test_graph_release_digest_mismatch_blocks_promotion(self):
        verifier = self.verified()
        result = PromotionEligibility().evaluate(
            promotion_evidence(verifier, "9" * 64)
        )
        self.assertFalse(result.eligible)
        self.assertIn("GRAPH_RELEASE_EVIDENCE_DIGEST_MISMATCH", result.reasons)

    def test_graph_release_verification_receipt_must_be_bound(self):
        verifier = self.verified()
        result = PromotionEligibility().evaluate(
            promotion_evidence(
                verifier,
                verifier["graph_release_evidence_digest"],
                verification_receipt_ids=("verify-other",),
            )
        )
        self.assertFalse(result.eligible)
        self.assertIn("GRAPH_RELEASE_VERIFICATION_RECEIPT_BINDING_REQUIRED", result.reasons)

    def test_valid_graph_release_can_become_promotion_eligible_without_promoting(self):
        verifier = self.verified()
        digest = verifier["graph_release_evidence_digest"]
        evidence = promotion_evidence(verifier, digest)
        result = PromotionEligibility().evaluate(evidence)
        self.assertTrue(result.eligible)

        machine = PromotionRollbackStateMachine(clock=lambda: "2026-10-04T16:00:00Z")
        intent = machine.create_promotion_intent(evidence)
        self.assertEqual("PROMOTION_PENDING", intent.state)
        self.assertEqual(digest, intent.graph_release_evidence_digest)
        self.assertEqual(verifier["verification_id"], intent.graph_release_verification_id)
        self.assertIsNone(machine.current_authority_sha)

    def test_promotion_receipt_schema_accepts_graph_release_binding(self):
        verifier = self.verified()
        evidence = promotion_evidence(verifier, verifier["graph_release_evidence_digest"])
        machine = PromotionRollbackStateMachine(clock=lambda: "2026-10-04T16:00:00Z")
        intent = machine.create_promotion_intent(evidence)
        schema = json.loads((ROOT / "schemas/gacm-run-state.schema.json").read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        state = json.loads((ROOT / "tests/fixtures/valid_new_run.json").read_text(encoding="utf-8"))
        state["promotion_history"] = [intent.to_dict()]
        errors = list(validator.iter_errors(state))
        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
