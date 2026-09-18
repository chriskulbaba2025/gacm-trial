import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "gacm-run-state.schema.json"
FIXTURES = ROOT / "tests" / "fixtures"


class GacmRunStateSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.validator = Draft202012Validator(cls.schema, format_checker=FormatChecker())

    def load(self, name):
        return json.loads((FIXTURES / name).read_text(encoding="utf-8"))

    def assert_valid_fixture(self, name):
        errors = sorted(self.validator.iter_errors(self.load(name)), key=lambda error: list(error.path))
        self.assertEqual([], errors, f"{name}: {errors}")

    def assert_invalid_fixture(self, name):
        errors = list(self.validator.iter_errors(self.load(name)))
        self.assertTrue(errors, f"{name} unexpectedly validated")

    def test_valid_newly_created_run(self):
        self.assert_valid_fixture("valid_new_run.json")

    def test_valid_multi_unit_running_state(self):
        self.assert_valid_fixture("valid_multi_unit_running.json")

    def test_valid_local_repair(self):
        self.assert_valid_fixture("valid_local_repair.json")

    def test_valid_broader_requalification(self):
        self.assert_valid_fixture("valid_broader_requalification.json")

    def test_valid_settle_state(self):
        self.assert_valid_fixture("valid_settle.json")

    def test_valid_rollback_state(self):
        self.assert_valid_fixture("valid_rollback.json")

    def test_invalid_executor_authored_authoritative_pass(self):
        self.assert_invalid_fixture("invalid_executor_pass.json")

    def test_invalid_ambiguous_operational_context(self):
        self.assert_invalid_fixture("invalid_ambiguous_context.json")

    def test_invalid_missing_rollback_authority(self):
        self.assert_invalid_fixture("invalid_missing_rollback.json")

    def test_invalid_illegal_lifecycle_transition(self):
        self.assert_invalid_fixture("invalid_illegal_transition.json")

    def test_schema_declares_finite_qualification_state(self):
        qualification = self.schema["$defs"]["qualificationState"]
        self.assertIn("graph", qualification["required"])
        self.assertIn("normative_requirement_ids", qualification["required"])
        self.assertIn("escape_scan_budget", qualification["required"])
        self.assertIn("pre_promotion", qualification["required"])

    def test_schema_declares_required_lifecycle_enums(self):
        lifecycle = self.schema["$defs"]["lifecycle"]["properties"]["status"]["enum"]
        verification = self.schema["$defs"]["verification"]["properties"]["status"]["enum"]
        self.assertEqual(
            ["CREATED", "READY", "RUNNING", "BLOCKED", "VERIFYING", "PROMOTION_PENDING", "SETTLING", "COMPLETE", "FAILED", "ROLLED_BACK"],
            lifecycle,
        )
        self.assertEqual(["NOT_RUN", "PASS", "FAIL", "BLOCKED", "UNOBSERVABLE"], verification)


if __name__ == "__main__":
    unittest.main()
