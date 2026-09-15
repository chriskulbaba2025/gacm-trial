import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gacm.promotion import PromotionRollbackStateMachine, PromotionState, PromotionTransitionError  # noqa: E402


SHA = "a" * 40
CANDIDATE = "b" * 40
TARGET = "c" * 40


def evidence(**overrides):
    value = {
        "run_id": "run-11", "candidate_sha": CANDIDATE, "candidate_artifact_identity": "artifact-b",
        "current_authoritative_sha": SHA, "rollback_target_sha": TARGET,
        "github_authority_status": "VERIFIED", "operational_context_status": "VERIFIED",
        "execution_status": "COMPLETED", "identity_validation_result": "VALID",
        "verification": {"status": "PASS", "authoritative": True, "issuer_role": "INDEPENDENT_VERIFIER"},
        "verification_receipt_ids": ("verify-1",), "operational_context_id": "ctx-1",
        "authority_continuity": True, "candidate_identity_matches": True,
        "known_good_targets": {TARGET: {"sha": TARGET}},
    }
    value.update(overrides)
    return value


class PromotionRollbackTests(unittest.TestCase):
    def setUp(self):
        self.clock = lambda: "2026-09-15T16:00:00Z"

    def test_eligibility_requires_all_governed_preconditions(self):
        machine = PromotionRollbackStateMachine(clock=self.clock)
        self.assertEqual("ELIGIBLE", machine.assess(evidence()).state)
        for key, value in (("verification", {}), ("execution_status", "FAILED"), ("identity_validation_result", "INVALID_PLACEHOLDER"), ("rollback_target_sha", None), ("candidate_sha", None), ("repair_required", True)):
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


if __name__ == "__main__": unittest.main()
