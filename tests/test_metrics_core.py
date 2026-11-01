import json
import tempfile
import unittest
from pathlib import Path

from gacm.metrics.guard import compare, inventory
from gacm.metrics.report import render_report
from gacm.metrics.run_record import build_record


class MetricsCoreTests(unittest.TestCase):
    def test_run_record_keeps_measurements_under_self_reported(self):
        record = build_record("MA-2", {"tokens_used": "UNAVAILABLE"})
        self.assertIn("self_reported", record)
        self.assertNotIn("checks", record)

    def test_report_unknown_without_tracing_or_pr(self):
        markdown, payload = render_report([build_record("MA-1A", {})], {"prs": None, "checks": None})
        self.assertIn("UNKNOWN", markdown)
        self.assertEqual("UNKNOWN", payload["runs"][0]["observed"]["first_push_green"])

    def test_report_marks_self_report_mismatch(self):
        record = build_record("MA-2", {"first_push_green": True})
        fixture = {"prs": [{"number": 2, "tranche_id": "MA-2", "head_shas": ["a"], "required_checks": ["gacm-gate"]}], "checks": {"a:gacm-gate": "failure"}}
        _, payload = render_report([record], fixture)
        self.assertEqual("DISCREPANCY", payload["runs"][0]["result"])

    def test_guard_counts_test_ids_and_assertions(self):
        ids, assertions, skips = inventory("def test_x():\n    assert True\n")
        self.assertEqual({"test_x"}, ids); self.assertEqual(1, assertions); self.assertEqual(0, skips)


if __name__ == "__main__": unittest.main()
