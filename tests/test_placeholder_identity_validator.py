import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gacm.identity_validation import PlaceholderIdentityValidator, ValidationResult  # noqa: E402
from gacm.repair import RepairScopePlanner  # noqa: E402
from gacm.execution import GCUExecutionAdapter, RunnerResult  # noqa: E402
from tests.test_gcu_execution_adapter import completed_runner, request  # noqa: E402


CONTEXT = {
    "status": "VERIFIED", "context_id": "ctx-1", "context_revision": "7", "authority_head": "head-1",
    "values": {"project": "project-a", "client": "client-a", "repository": "repo-a", "branch": "main", "environment": "staging", "cloud_account": {"account_id": "acct-a"}, "tenant": "tenant-a", "region": "ca-central-1", "deployment_target": "deploy-a", "service": "api", "database": "db-a", "domain": "example.test"},
    "sources": [{"source_kind": "GITHUB", "source_path": "contexts/a.json"}],
}


class IdentityValidatorTests(unittest.TestCase):
    def setUp(self):
        self.validator = PlaceholderIdentityValidator(clock=lambda: "2026-09-15T15:00:00Z")

    def validate(self, output, classes=("account",), **kwargs):
        return self.validator.validate(operational_context=CONTEXT, output=output, required_identity_classes=classes, run_id="run-10", work_unit_id="unit-1", **kwargs)

    def test_authoritative_and_placeholder_cases(self):
        self.assertEqual("VALID", self.validate("account_id=acct-a").result)
        self.assertEqual("INVALID_PLACEHOLDER", self.validate("account_id=<ACCOUNT_ID>").result)
        self.assertEqual("INVALID_PLACEHOLDER", self.validate("region=YOUR_REGION", ("region",)).result)
        self.assertEqual("INVALID_PLACEHOLDER", self.validate("repo=<REPO>", ("repository",)).result)
        self.assertEqual("INVALID_PLACEHOLDER", self.validate("What is your account ID?").result)
        self.assertEqual("INVALID_PLACEHOLDER", self.validate("tenant=example-tenant", ("tenant",)).result)

    def test_identity_scope_provenance_and_stale_cases(self):
        self.assertEqual("INVALID_IDENTITY", self.validate("account_id=acct-b").result)
        self.assertEqual("INVALID_SCOPE", self.validate("account_id=acct-project-b", active_project="project-a").result)
        self.assertEqual("INVALID_SCOPE", self.validate("environment=production", ("environment",), active_environment="staging").result)
        self.assertEqual("INVALID_IDENTITY", self.validate("account_id=acct-memory", source_provenance="CHAT").result)
        self.assertEqual("BLOCKED", self.validate("account_id=acct-a", context_snapshot_revision="8").result)
        missing = dict(CONTEXT); missing["values"] = dict(CONTEXT["values"]); del missing["values"]["region"]
        self.assertEqual("BLOCKED", self.validator.validate(operational_context=missing, output="region=x", required_identity_classes=("region",), run_id="r", work_unit_id="u").result)

    def test_unobservable_multi_identity_determinism_and_receipt(self):
        self.assertEqual("UNOBSERVABLE", self.validate(object(), ("account",)).result)
        first = self.validate("account_id=acct-a region=ca-central-1", ("account", "region")).to_dict()
        second = self.validate("account_id=acct-a region=ca-central-1", ("account", "region")).to_dict()
        self.assertEqual(first, second)
        receipt = self.validate("account_id=acct-a")
        self.assertFalse(receipt.authoritative)
        projection = receipt.to_run_state_projection()
        state = json.loads((ROOT / "tests/fixtures/valid_new_run.json").read_text(encoding="utf-8"))
        state.setdefault("evidence", []).append(projection["evidence"])
        state["identity_validations"] = [projection["identity_validation"]]
        errors = list(Draft202012Validator(json.loads((ROOT / "schemas/gacm-run-state.schema.json").read_text()), format_checker=FormatChecker()).iter_errors(state))
        self.assertEqual([], errors)

    def test_phase_9_local_and_authority_scope(self):
        local = RepairScopePlanner(clock=lambda: "2026-09-15T15:00:00Z").plan(verification_receipt={"run_id": "r", "work_unit_id": "u"}, actual_changed_paths=("src/u.py",), work_units=({"unit_id": "u", "allowed_surfaces": ["src/u.py"], "dependencies": []},), surface_flags={})
        self.assertEqual("LOCAL", local.classification)
        authority = RepairScopePlanner(clock=lambda: "2026-09-15T15:00:00Z").plan(verification_receipt={"run_id": "r", "work_unit_id": "u"}, actual_changed_paths=("identity/context.py",), work_units=({"unit_id": "u", "allowed_surfaces": ["identity/context.py"], "dependencies": []},), surface_flags={"authority": True})
        self.assertTrue(authority.authority_revalidation_required)

    def test_gcu_output_cannot_bypass_validator_before_phase8(self):
        adapter = GCUExecutionAdapter(identity_validator=self.validator, clock=lambda: "2026-09-15T15:00:00Z")
        execution_context = dict(CONTEXT, context_revision="1")
        req = request(operational_context=execution_context, required_identity_classes=("account",))
        bad = adapter.execute(req, completed_runner(commands_executed=("deploy --account <ACCOUNT_ID>",)))
        self.assertEqual("FAILED", bad.execution_status)
        self.assertTrue(any(item.get("result") == "INVALID_PLACEHOLDER" for item in bad.evidence_artifacts))
        good = adapter.execute(req, completed_runner(commands_executed=("deploy --account acct-a",)))
        self.assertEqual("COMPLETED", good.execution_status)


if __name__ == "__main__":
    unittest.main()
