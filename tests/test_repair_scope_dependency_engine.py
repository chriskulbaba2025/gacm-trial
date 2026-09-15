import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gacm.repair import BLOCKED_FOR_SCOPE_RESOLUTION, RepairScopePlanner  # noqa: E402


def receipt(**changes):
    value = {"run_id": "run-9", "work_unit_id": "u1", "affected_scope_determination": {"classification": "LOCAL"}}
    value.update(changes)
    return value


UNITS = (
    {"unit_id": "u1", "allowed_surfaces": ["src/a.py"], "dependencies": [], "tests": ["t1"]},
    {"unit_id": "u2", "allowed_surfaces": ["src/b.py"], "dependencies": ["u1"], "tests": ["t2"]},
    {"unit_id": "u3", "allowed_surfaces": ["src/c.py"], "dependencies": ["u2"], "tests": ["t3"]},
    {"unit_id": "u4", "allowed_surfaces": ["src/d.py"], "dependencies": [], "tests": ["t4"]},
)


ASSURANCE = (
    {"assurance_id": "a1", "work_unit_id": "u1", "surfaces": ["src/a.py"], "rerun_scope": ["t1"]},
    {"assurance_id": "a2", "work_unit_id": "u2", "surfaces": ["src/b.py"], "rerun_scope": ["t2"]},
    {"assurance_id": "a4", "work_unit_id": "u4", "surfaces": ["src/d.py"], "rerun_scope": ["t4"]},
)


class RepairScopeTests(unittest.TestCase):
    def setUp(self):
        self.planner = RepairScopePlanner(clock=lambda: "2026-09-14T15:00:00Z")

    def plan(self, paths, **kwargs):
        return self.planner.plan(receipt(), actual_changed_paths=paths, work_units=UNITS, prior_pass_receipts=ASSURANCE, **kwargs)

    def test_local_repair_only_invalidates_one_unit_and_preserves_unrelated(self):
        plan = self.plan(("src/a.py",))
        self.assertEqual("LOCAL", plan.classification)
        self.assertEqual(("u1",), plan.directly_affected_work_units)
        self.assertEqual(("u2", "u3"), plan.transitively_affected_work_units)
        self.assertEqual(("a1", "a2"), plan.assurance_invalidated)
        self.assertEqual(("a4",), plan.assurance_preserved)
        self.assertFalse(plan.full_run_replay_required)

    def test_dependency_closure_and_unrelated_branch(self):
        plan = self.plan(("src/a.py",))
        self.assertEqual(("t1", "t2", "t3"), plan.tests_to_rerun)
        # A local surface alone does not expand; an explicit dependency surface does.
        expanded = self.plan(("shared/lib.py",), surface_flags={"dependency": True})
        self.assertEqual("DEPENDENCY_EXPANDED", expanded.classification)
        self.assertEqual(("u1",), expanded.directly_affected_work_units)
        self.assertIn("u3", expanded.transitively_affected_work_units)
        self.assertIn("a4", expanded.assurance_preserved)

    def test_authority_model_architecture_and_unknown(self):
        authority = self.plan(("config/context.json",), surface_flags={"authority": True})
        self.assertEqual("AUTHORITY_BEARING", authority.classification)
        self.assertTrue(authority.authority_revalidation_required)
        model = self.plan(("prompts/router.txt",), surface_flags={"model": True})
        self.assertTrue(model.model_requalification_required)
        architecture = self.plan(("src/a.py",), surface_flags={"architecture": True})
        self.assertTrue(architecture.architecture_requalification_required)
        self.assertFalse(architecture.full_run_replay_required)
        unknown = self.plan(None)
        self.assertEqual(BLOCKED_FOR_SCOPE_RESOLUTION, unknown.status)

    def test_graphify_only_is_ignored_but_git_evidence_counts(self):
        graph = [{"source_kind": "GRAPHIFY", "from_unit": "u1", "to_unit": "u4", "corroborated": False, "evidence_id": "g"}]
        plan = self.plan(("src/a.py",), dependency_evidence=graph)
        self.assertNotIn("u4", plan.transitively_affected_work_units)
        git = [{"source_kind": "GIT", "source_ref": "git:deps", "from_unit": "u1", "to_unit": "u4", "corroborated": True}]
        plan = self.plan(("src/a.py",), dependency_evidence=git)
        self.assertIn("u4", plan.transitively_affected_work_units)

    def test_verifier_is_cross_checked_executor_claim_is_not_used(self):
        plan = self.planner.plan(receipt(affected_scope_determination={"classification": "AUTHORITY_BEARING"}), actual_changed_paths=("src/a.py",), work_units=UNITS, prior_pass_receipts=ASSURANCE)
        self.assertEqual("LOCAL", plan.classification)
        plan = self.planner.plan(receipt(), actual_changed_paths=("src/a.py",), work_units=UNITS, prior_pass_receipts=ASSURANCE, repair_scope_classification="ARCHITECTURE_BEARING")
        self.assertEqual("LOCAL", plan.classification)

    def test_historical_pass_is_distinct_from_current_reliability_and_projection_validates(self):
        plan = self.plan(("src/a.py",))
        self.assertEqual(("a1", "a2", "a4"), plan.historical_pass_receipts)
        self.assertEqual(("a4",), plan.currently_reliable_assurance)
        state = json.loads((ROOT / "tests/fixtures/valid_multi_unit_running.json").read_text(encoding="utf-8"))
        projection = plan.to_run_state_projection()
        state.setdefault("evidence", []).append(projection["evidence"])
        state["repair_plans"] = [projection["repair_plan"]]
        errors = list(Draft202012Validator(json.loads((ROOT / "schemas/gacm-run-state.schema.json").read_text()), format_checker=FormatChecker()).iter_errors(state))
        self.assertEqual([], errors)

    def test_whole_closure_requires_full_replay_but_engine_cannot_pass(self):
        plan = self.plan(("src/a.py",), surface_flags={"dependency": True})
        # u4 is independent, so the closure is not the whole run.
        self.assertFalse(plan.full_run_replay_required)
        all_units = tuple(dict(u, dependencies=["u1"] if u["unit_id"] == "u4" else u["dependencies"]) for u in UNITS)
        plan = self.planner.plan(receipt(), actual_changed_paths=("src/a.py",), work_units=all_units, prior_pass_receipts=ASSURANCE, surface_flags={"dependency": True})
        self.assertTrue(plan.full_run_replay_required)
        self.assertNotIn("PASS", plan.status)


if __name__ == "__main__":
    unittest.main()
