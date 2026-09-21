import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gacm.generalization import GATE_ID, GeneralizationGate  # noqa: E402
from gacm.promotion import PromotionRollbackStateMachine, PromotionState, PromotionTransitionError, SettlePolicy  # noqa: E402


SHA = "a" * 40
CANDIDATE = "b" * 40
TARGET = "c" * 40


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
        "issuer_role": "INDEPENDENT_VERIFIER", "authoritative": True,
        "contract_digest": digest, "acceptance_boundary_unchanged": True,
        "system_map_status": "PASS", "whole_authorized_scope_closed": True,
        "closure_definition_of_done_met": True,
        "generalized_scenarios": [
            {"scenario_id": "fresh-a", "input_identity": "a", "materially_different": True, "reference_fixture": False, "runtime_path_identity": "generic", "boundary_results": {"input": "PASS", "processing": "PASS", "output": "PASS"}, "evidence_ids": ["fresh-a"]},
            {"scenario_id": "fresh-b", "input_identity": "b", "materially_different": True, "reference_fixture": False, "runtime_path_identity": "generic", "boundary_results": {"input": "PASS", "processing": "PASS", "output": "PASS"}, "evidence_ids": ["fresh-b"]},
        ],
        "fixture_dependency_scan": {"status": "PASS", "scanner_id": "scan", "scanned_paths": ["src/product.py"], "findings": [], "evidence_ids": ["scan"]},
        "reference_regression": {"status": "PASS", "evidence_ids": ["reference"]},
        "full_regression": {"status": "PASS", "evidence_ids": ["full"]},
    }
    return contract, evidence


def evidence(**overrides):
    generalization_contract, generalization_evidence = generalization_pair()
    value = {
        "run_id": "run-11", "candidate_sha": CANDIDATE, "candidate_artifact_identity": "artifact-b",
        "current_authoritative_sha": SHA, "rollback_target_sha": TARGET,
        "github_authority_status": "VERIFIED", "operational_context_status": "VERIFIED",
        "execution_status": "COMPLETED", "identity_validation_result": "VALID",
        "verification": {"status": "PASS", "authoritative": True, "issuer_role": "INDEPENDENT_VERIFIER"},
        "verification_receipt_ids": ("verify-1",), "operational_context_id": "ctx-1",
        "authority_continuity": True, "candidate_identity_matches": True,
        "known_good_targets": {TARGET: {"sha": TARGET}},
        "generalization_contract": generalization_contract,
        "generalization_evidence": generalization_evidence,
    }
    value.update(overrides)
    return value


class PromotionRollbackTests(unittest.TestCase):
    def setUp(self):
        self.clock = lambda: "2026-09-15T16:00:00Z"

    def test_eligibility_requires_all_governed_preconditions(self):
        machine = PromotionRollbackStateMachine(clock=self.clock)
        self.assertEqual("ELIGIBLE", machine.assess(evidence()).state)
        for key, value in (("verification", {}), ("execution_status", "FAILED"), ("identity_validation_result", "INVALID_PLACEHOLDER"), ("rollback_target_sha", None), ("candidate_sha", None), ("repair_required", True), ("generalization_evidence", {})):
            result = machine.assess(evidence(**{key: value}))
            self.assertIn(result.state, {"NOT_ELIGIBLE", "BLOCKED"})

    def test_intent_precedes_promotion_and_preserves_prior_authority(self):
        machine = PromotionRollbackStateMachine(clock=self.clock)
        intent = machine.create_promotion_intent(evidence())
        self.assertEqual("PROMOTION_PENDING", intent.state)
        self.assertEqual(SHA, intent.prior_authoritative_sha)
        promoted = machine.promote(current_authoritative_sha=SHA)
        self.assertEqual("PROMOTED", promoted.state)
        self.assertEqual(CANDIDATE, machine.current_authority_sha)
        self.assertEqual(2, len(machine.promotion_history))

    def test_settle_required_and_complete_is_phase12_only(self):
        machine = PromotionRollbackStateMachine(clock=self.clock)
        machine.create_promotion_intent(evidence(settle_required=True))
        promoted = machine.promote(current_authoritative_sha=SHA)
        self.assertEqual("SETTLE_REQUIRED", promoted.state)
        with self.assertRaises(PromotionTransitionError): machine.mark_complete()

    def test_authority_continuity_and_actor_boundaries(self):
        machine = PromotionRollbackStateMachine(clock=self.clock)
        with self.assertRaises(PromotionTransitionError): machine.create_promotion_intent(evidence(authority_continuity=False))
        with self.assertRaises(PromotionTransitionError): machine.create_promotion_intent(evidence(), actor_role="EXECUTOR")
        with self.assertRaises(PromotionTransitionError): machine.create_promotion_intent(evidence(), actor_role="INDEPENDENT_VERIFIER")
        machine.create_promotion_intent(evidence())
        with self.assertRaises(PromotionTransitionError): machine.promote(current_authoritative_sha=TARGET)

    def test_human_gate_and_stale_verification(self):
        machine = PromotionRollbackStateMachine(clock=self.clock)
        with self.assertRaises(PromotionTransitionError): machine.create_promotion_intent(evidence(human_approval_required=True))
        approved = machine.create_promotion_intent(evidence(human_approval_required=True, human_approval="human-1"))
        self.assertEqual("PROMOTION_PENDING", approved.state)

    def test_rollback_requires_known_target_and_preserves_history(self):
        machine = PromotionRollbackStateMachine(clock=self.clock)
        machine.create_promotion_intent(evidence())
        machine.promote(current_authoritative_sha=SHA)
        with self.assertRaises(PromotionTransitionError): machine.request_rollback(run_id="run-11", current_authoritative_sha=CANDIDATE, rollback_target_sha="d" * 40, known_good_targets={}, reason="failed observation")
        pending = machine.request_rollback(run_id="run-11", current_authoritative_sha=CANDIDATE, rollback_target_sha=TARGET, known_good_targets={TARGET: {}}, reason="failed observation", preserved_verification_receipt_ids=("verify-1",))
        self.assertEqual("ROLLBACK_PENDING", pending.state)
        rolled = machine.execute_rollback(rollback_id=pending.rollback_id, current_authoritative_sha=CANDIDATE)
        self.assertEqual("ROLLED_BACK", rolled.state)
        self.assertEqual(TARGET, machine.current_authority_sha)
        self.assertEqual(("verify-1",), rolled.preserved_verification_receipt_ids)
        self.assertEqual(2, len(machine.rollback_history))

    def test_illegal_duplicate_and_continuation_transitions_rejected(self):
        machine = PromotionRollbackStateMachine(clock=self.clock)
        with self.assertRaises(PromotionTransitionError): machine.promote(current_authoritative_sha=SHA)
        machine.create_promotion_intent(evidence())
        machine.promote(current_authoritative_sha=SHA)
        with self.assertRaises(PromotionTransitionError): machine.promote(current_authoritative_sha=SHA)
        pending = machine.request_rollback(run_id="run-11", current_authoritative_sha=CANDIDATE, rollback_target_sha=TARGET, known_good_targets={TARGET: {}}, reason="rollback")
        machine.execute_rollback(rollback_id=pending.rollback_id, current_authoritative_sha=CANDIDATE)
        with self.assertRaises(PromotionTransitionError): machine.execute_rollback(rollback_id=pending.rollback_id, current_authoritative_sha=CANDIDATE)

    def test_receipts_are_deterministic_and_project_durably(self):
        first = PromotionRollbackStateMachine(clock=self.clock); i1 = first.create_promotion_intent(evidence()); p1 = first.promote(current_authoritative_sha=SHA)
        second = PromotionRollbackStateMachine(clock=self.clock); i2 = second.create_promotion_intent(evidence()); p2 = second.promote(current_authoritative_sha=SHA)
        self.assertEqual(i1.to_dict(), i2.to_dict()); self.assertEqual(p1.to_dict(), p2.to_dict())
        state = json.loads((ROOT / "tests/fixtures/valid_new_run.json").read_text(encoding="utf-8"))
        for item in (i1.to_run_state_projection(), p1.to_run_state_projection()):
            state.setdefault("evidence", []).append(item["evidence"])
            state.setdefault("promotion_history", []).extend(item["promotion_history"])
        errors = list(Draft202012Validator(json.loads((ROOT / "schemas/gacm-run-state.schema.json").read_text()), format_checker=FormatChecker()).iter_errors(state))
        self.assertEqual([], errors)

    def test_rollback_projection_and_no_evidence_rewrite(self):
        machine = PromotionRollbackStateMachine(clock=self.clock)
        machine.create_promotion_intent(evidence())
        machine.promote(current_authoritative_sha=SHA)
        pending = machine.request_rollback(run_id="run-11", current_authoritative_sha=CANDIDATE, rollback_target_sha=TARGET, known_good_targets={TARGET: {}}, reason="failed settle", preserved_verification_receipt_ids=("verify-1",))
        rolled = machine.execute_rollback(rollback_id=pending.rollback_id, current_authoritative_sha=CANDIDATE)
        projection = rolled.to_run_state_projection()
        self.assertEqual("ROLLBACK_RECEIPT", projection["evidence"]["kind"])
        self.assertEqual(("verify-1",), rolled.preserved_verification_receipt_ids)
        self.assertEqual(2, len(machine.promotion_history))

    def _settle_machine(self, **overrides):
        machine = PromotionRollbackStateMachine(clock=self.clock)
        machine.create_promotion_intent(evidence(settle_required=True, **overrides))
        machine.promote(current_authoritative_sha=SHA)
        return machine

    def test_valid_settle_entry_binds_exact_identity_and_receipt(self):
        machine = self._settle_machine()
        policy = SettlePolicy("policy-v1", "1", ("health",), optional_checks=("latency",))
        settle_id = machine.begin_settle(policy, current_authoritative_sha=CANDIDATE)
        self.assertEqual("OBSERVING", machine.state)
        self.assertTrue(settle_id.startswith("settle-"))
        self.assertEqual(CANDIDATE, machine.settle["candidate_sha"])
        self.assertEqual(SHA, machine.settle["prior_authoritative_sha"])
        self.assertEqual(0, len(machine.settle_history))

    def test_settle_entry_missing_required_phase_or_rollback_or_changed_authority_blocks(self):
        machine = PromotionRollbackStateMachine(clock=self.clock)
        machine.create_promotion_intent(evidence(settle_required=True)); machine.promote(current_authoritative_sha=SHA)
        machine.intent["rollback_target_sha"] = None
        with self.assertRaises(PromotionTransitionError): machine.begin_settle(SettlePolicy("p", "1", ("health",)), current_authoritative_sha=CANDIDATE)
        self.assertEqual("BLOCKED", machine.state)
        machine = self._settle_machine()
        with self.assertRaises(PromotionTransitionError): machine.begin_settle(SettlePolicy("p", "1", ("health",)), current_authoritative_sha=TARGET)
        self.assertEqual("BLOCKED", machine.state)

    def test_settle_pass_then_stable_only_after_observation(self):
        machine = self._settle_machine()
        with self.assertRaises(PromotionTransitionError): machine.stabilize(current_authoritative_sha=CANDIDATE)
        machine.begin_settle(SettlePolicy("p", "1", ("health",)), current_authoritative_sha=CANDIDATE)
        observed = machine.observe_settle({"health": True}, current_authoritative_sha=CANDIDATE, evidence_references=("obs-1",))
        self.assertEqual("OBSERVING", observed.state)
        passed = machine.finalize_settle(current_authoritative_sha=CANDIDATE)
        self.assertEqual("SETTLE_PASS", passed.state); self.assertEqual("PASS", passed.result)
        machine.stabilize(current_authoritative_sha=CANDIDATE)
        self.assertEqual("STABLE", machine.state)
        self.assertEqual(CANDIDATE, passed.candidate_sha)

    def test_settle_fail_requires_existing_phase11_rollback(self):
        machine = self._settle_machine()
        machine.begin_settle(SettlePolicy("p", "1", ("health",)), current_authoritative_sha=CANDIDATE)
        failed = machine.observe_settle({"health": False}, current_authoritative_sha=CANDIDATE, evidence_references=("failure-1",))
        self.assertEqual("SETTLE_FAIL", failed.state); self.assertEqual("ROLLBACK_REQUIRED", failed.next_governed_action); self.assertEqual("ROLLBACK_REQUIRED", machine.state)
        pending = machine.request_rollback(run_id="run-11", current_authoritative_sha=CANDIDATE, rollback_target_sha=TARGET, known_good_targets={TARGET: {}}, reason="settle failed", preserved_verification_receipt_ids=("verify-1",))
        self.assertEqual("ROLLBACK_PENDING", pending.state)

    def test_missing_mandatory_observation_and_contradictory_authority_fail_closed(self):
        machine = self._settle_machine(); machine.begin_settle(SettlePolicy("p", "1", ("health", "errors")), current_authoritative_sha=CANDIDATE)
        missing = machine.observe_settle({"health": True}, current_authoritative_sha=CANDIDATE)
        self.assertEqual("SETTLE_FAIL", missing.state); self.assertEqual("MANDATORY_OBSERVATION_MISSING", missing.failure_reason); self.assertEqual("ROLLBACK_REQUIRED", machine.state)
        machine = self._settle_machine(); machine.begin_settle(SettlePolicy("p", "1", ("health",)), current_authoritative_sha=CANDIDATE)
        blocked = machine.observe_settle({"health": True}, current_authoritative_sha=TARGET, evidence_references=("contradiction",))
        self.assertEqual("BLOCKED", blocked.state); self.assertEqual("AUTHORITY_CHANGED_DURING_OBSERVATION", blocked.failure_reason)

    def test_duplicate_observation_is_idempotent_and_history_is_append_only(self):
        machine = self._settle_machine(); machine.begin_settle(SettlePolicy("p", "1", ("health",)), current_authoritative_sha=CANDIDATE)
        first = machine.observe_settle({"health": True}, current_authoritative_sha=CANDIDATE, evidence_references=("obs-1",))
        duplicate = machine.observe_settle({"health": True}, current_authoritative_sha=CANDIDATE, evidence_references=("obs-1",))
        self.assertEqual(first.to_dict(), duplicate.to_dict()); self.assertEqual(1, len(machine.settle_history))
        machine.finalize_settle(current_authoritative_sha=CANDIDATE); machine.stabilize(current_authoritative_sha=CANDIDATE)
        self.assertEqual("STABLE", machine.state)

    def test_invalid_policy_and_exact_identity_mismatch(self):
        with self.assertRaises(ValueError): SettlePolicy("", "1", ("health",))
        with self.assertRaises(ValueError): SettlePolicy("p", "1", ("health",), optional_checks=("health",))
        machine = self._settle_machine(); machine.begin_settle(SettlePolicy("p", "1", ("health",)), current_authoritative_sha=CANDIDATE)
        mismatch = machine.observe_settle({"other": True}, current_authoritative_sha=CANDIDATE)
        self.assertEqual("SETTLE_FAIL", mismatch.state); self.assertEqual("UNKNOWN_CHECK", mismatch.failure_reason)


if __name__ == "__main__": unittest.main()
