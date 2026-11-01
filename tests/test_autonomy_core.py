import unittest

from gacm.metrics.autonomy import (
    allowed_at_level,
    approval_matches,
    independent_approval_matches,
    codeowners_exceptions,
    parse_level,
    recommend,
    risk_class,
    validate_codeowners,
)
from gacm.metrics.report import render_report
from gacm.metrics.run_record import build_record


class AutonomyCoreTests(unittest.TestCase):
    def test_unlisted_and_not_a_tranche_are_high(self):
        self.assertEqual("high", risk_class(["policy/autonomy.json"], {"low": ["tests/**"], "medium": ["src/**"]}))
        self.assertEqual("high", risk_class([], {}, not_a_tranche=True))

    def test_class_is_highest_changed_path(self):
        self.assertEqual("medium", risk_class(["tests/test_x.py", "src/gacm/new.py"], {"low": ["tests/**"], "medium": ["src/**"]}))

    def test_level_invalid_defaults_to_zero_and_permissions_hold(self):
        self.assertEqual(0, parse_level("bad"))
        self.assertTrue(allowed_at_level("low", 1))
        self.assertFalse(allowed_at_level("medium", 1))
        self.assertFalse(allowed_at_level("high", 2))

    def test_stale_or_non_owner_approval_does_not_match(self):
        reviews = [{"user": {"login": "other"}, "state": "APPROVED", "commit_id": "head"}, {"user": {"login": "chriskulbaba2025"}, "state": "APPROVED", "commit_id": "old"}]
        self.assertFalse(approval_matches(reviews, "chriskulbaba2025", "head"))

    def test_independent_current_head_approval_matches(self):
        reviews = [{"user": {"login": "reviewer"}, "state": "APPROVED", "commit_id": "head"}]
        self.assertTrue(independent_approval_matches(reviews, "head", "chriskulbaba2025"))
        self.assertFalse(independent_approval_matches(reviews, "old", "chriskulbaba2025"))

    def test_author_cannot_satisfy_independent_approval(self):
        reviews = [{"user": {"login": "chriskulbaba2025"}, "state": "APPROVED", "commit_id": "head"}]
        self.assertFalse(independent_approval_matches(reviews, "head", "chriskulbaba2025"))

    def test_codeowners_must_match_risk_exceptions(self):
        risk = {"low": ["tests/test_*.py"], "medium": ["src/gacm/**/*.py"]}
        owners = "* @chriskulbaba2025\ntests/test_*.py\nsrc/gacm/**/*.py\n"
        self.assertEqual({"tests/test_*.py", "src/gacm/**/*.py"}, codeowners_exceptions(owners))
        self.assertTrue(validate_codeowners(owners, risk))

    def test_unknown_or_discrepancy_blocks_promotion(self):
        stats = {"low": {"measured_runs": 5, "first_push_green": 5, "escapes": 0, "discrepancies": 1}}
        self.assertEqual("DEMOTE to 0", recommend(0, stats))

    def test_unknown_escape_does_not_promote(self):
        record = build_record("MA-3", {"computed_risk_class": "low", "changed_lines": 100})
        _, payload = render_report([record], {"prs": None, "checks": None, "autonomy_level": 0})
        self.assertEqual("HOLD at 0", payload["autonomy"]["recommendations"]["low"])


if __name__ == "__main__":
    unittest.main()
