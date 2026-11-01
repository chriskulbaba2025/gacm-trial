import tempfile
import unittest
from pathlib import Path

from gacm.generalization import GATE_ID, GeneralizationGate
from gacm.harness import HarnessAdapters, HarnessConfig, JsonRunStateStore, MemoryRunStateStore, PilotHarness, PilotState, TopLevelState


SHA = "a" * 40


def generalization_contract():
    return {
        "gate_id": GATE_ID,
        "mode": "GENERALIZED",
        "product_definition_of_done": "Variable valid inputs traverse the capability end-to-end.",
        "authorized_capability_scope": ["capability"],
        "connected_system_path": ["input", "processing", "output"],
        "required_full_path_boundaries": ["input", "processing", "output"],
        "minimum_fresh_scenarios": 2,
        "reference_regression_ids": ["reference-case"],
    }


def generalization_evidence(c):
    digest = GeneralizationGate().contract_digest(c)
    return {
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


def config(**kwargs):
    values = dict(project_id="synthetic", prd_identity="prd-v1", authoritative_start_sha=SHA,
                  branch_or_worktree="isolated", gacm_version="4.2.2", execution_policy={},
                  human_authority={"promotion_required": False}, discovery_config={},
                  operational_context_requirements={}, generalization_contract=generalization_contract())
    values.update(kwargs)
    return HarnessConfig(**values)


class PilotHarnessTests(unittest.TestCase):
    def make(self, verify_status="PASS", settle_outcome="PASS", authority="VERIFIED", context="VERIFIED", route=True, broad=False, always_fail=False):
        store = MemoryRunStateStore(); calls = {"execute": 0, "verify": 0}
        def authority_fn(c): return {"status": authority, "sha": SHA}
        def context_fn(c, a, d): return {"status": context, "context_id": "ctx-1"}
        def route_fn(u): return {"selected_model": "Luna", "qualification_identity": "qual-1"} if route else {"selected_model": "Luna"}
        def execute(u, r, c): calls["execute"] += 1; return {"execution_status": "COMPLETED", "ending_sha": SHA}
        def verify(u, e, c): calls["verify"] += 1; return {"status": verify_status if always_fail or calls["verify"] == 1 else "PASS", "issuer_role": "INDEPENDENT_VERIFIER"}
        def repair_plan(u, v, s): return {"status": "PLANNED", "classification": "BROADER_REQUALIFICATION" if broad else "LOCAL"}
        def repair(u, p, c): return {"execution_status": "COMPLETED", "ending_sha": SHA}
        def identity(u, c): return {"result": "VALID"}
        def gen(s, c): return generalization_evidence(c)
        def promotion(s, h): return {"state": "SETTLE_REQUIRED"}
        def settle(s, p): return {"status": "SETTLE_PASS" if settle_outcome == "PASS" else "SETTLE_FAIL"}
        def rollback(s, r): return {"state": "ROLLED_BACK"}
        adapters = HarnessAdapters(authority_fn, lambda c, a: {"status": "DISCOVERED"}, context_fn,
                                   lambda c, x, w: [{"unit_id": "u1", "title": "unit", "status": "PENDING"}],
                                   route_fn, execute, verify, repair_plan, repair, identity_validate=identity, promotion=promotion,
                                   settle=settle, rollback=rollback, generalization_evidence=gen)
        return PilotHarness(adapters, store), config(), calls, store

    def test_clean_pass_and_resume_is_durable(self):
        h, c, calls, store = self.make()
        result = h.run(c, [{"unit_id": "u1"}])
        self.assertEqual(result["state"], TopLevelState.COMPLETED.value); self.assertEqual(calls["execute"], 1)
        again = h.run(c, run_id=result["run_id"], resume=True)
        self.assertEqual(again, result); self.assertEqual(calls["execute"], 1)

    def test_local_repair_and_broader_trigger_are_preserved(self):
        h, c, calls, _ = self.make(verify_status="FAIL", broad=True)
        result = h.run(c, [{"unit_id": "u1"}])
        self.assertEqual(result["state"], "COMPLETED"); self.assertTrue(result["receipts"]["repair"])

    def test_authority_and_model_blocks_prevent_execution(self):
        h, c, calls, _ = self.make(authority="AMBIGUOUS")
        self.assertEqual(h.run(c, [{"unit_id": "u1"}])["state"], "BLOCKED"); self.assertEqual(calls["execute"], 0)
        h, c, calls, _ = self.make(route=False)
        self.assertEqual(h.run(c, [{"unit_id": "u1"}])["state"], "BLOCKED"); self.assertEqual(calls["execute"], 0)

    def test_settle_failure_requires_rollback(self):
        h, c, _, _ = self.make(settle_outcome="FAIL")
        result = h.run(c, [{"unit_id": "u1"}])
        self.assertEqual(result["state"], "ROLLBACK_REQUIRED"); self.assertTrue(result["receipts"]["rollback"])

    def test_missing_generalization_evidence_blocks_before_promotion(self):
        h, c, _, _ = self.make()
        h.adapters = HarnessAdapters(
            h.adapters.authority, h.adapters.discovery, h.adapters.context, h.adapters.plan,
            h.adapters.route, h.adapters.execute, h.adapters.verify, h.adapters.repair_plan,
            h.adapters.repair, h.adapters.identity_validate, h.adapters.promotion, h.adapters.settle,
            h.adapters.rollback, h.adapters.current_authority, h.adapters.human_approval,
            generalization_evidence=None,
        )
        result = h.run(c, [{"unit_id": "u1"}])
        self.assertEqual("BLOCKED", result["state"])
        self.assertTrue(any("GENERALIZATION_EVIDENCE_ADAPTER_MISSING" in item for item in result["blockers"]))

    def test_human_gate(self):
        h, c, _, _ = self.make(); c = config(human_authority={"promotion_required": True})
        paused = h.run(c, [{"unit_id": "u1"}]); self.assertEqual(paused["state"], "PROMOTION_PENDING")
        done = h.run(c, run_id=paused["run_id"], resume=True, human_approval=True)
        self.assertEqual(done["state"], "COMPLETED")

    def test_resume_from_executed_unit_does_not_execute_again(self):
        h, c, calls, store = self.make()
        state = PilotState("interrupted", c, state=TopLevelState.EXECUTING)
        state.evidence = [{"kind": "context", "value": {"status": "VERIFIED", "context_id": "ctx-1"}}]
        state.units = [{
            "unit_id": "u1", "status": "EXECUTED",
            "route": {"selected_model": "Luna", "qualification_identity": "qual-1"},
            "execution": {"execution_status": "COMPLETED", "ending_sha": SHA},
        }]
        store.save(state.snapshot())
        result = h.run(c, run_id="interrupted", resume=True)
        self.assertEqual(result["state"], TopLevelState.COMPLETED.value)
        self.assertEqual(calls["execute"], 0)

    def test_repair_attempts_survive_resume_and_block_at_three(self):
        h, c, calls, store = self.make(verify_status="FAIL", always_fail=True)
        state = PilotState("capped", c, state=TopLevelState.EXECUTING)
        state.evidence = [{"kind": "context", "value": {"status": "VERIFIED", "context_id": "ctx-1"}}]
        state.units = [{
            "unit_id": "u1", "status": "EXECUTED",
            "route": {"selected_model": "Luna", "qualification_identity": "qual-1"},
            "execution": {"execution_status": "COMPLETED", "ending_sha": SHA},
        }]
        state.repair_attempts_by_family["VERIFICATION_FAILURE"] = 2
        state.repair_attempts_by_unit["u1"] = 2
        store.save(state.snapshot())
        result = h.run(c, run_id="capped", resume=True)
        self.assertEqual(result["state"], TopLevelState.BLOCKED.value)
        self.assertEqual(len(result["receipts"]["repair"]), 1)
        self.assertEqual(result["repair_attempts_by_family"]["VERIFICATION_FAILURE"], 3)

    def test_corrupt_json_state_holds(self):
        with tempfile.TemporaryDirectory() as directory:
            store = JsonRunStateStore(Path(directory))
            (Path(directory) / "broken.json").write_text("{", encoding="utf-8")
            h, c, _, _ = self.make()
            h.store = store
            result = h.run(c, run_id="broken", resume=True)
            self.assertEqual(result["state"], TopLevelState.BLOCKED.value)
            self.assertTrue(any("CORRUPT_DURABLE_STATE" in item for item in result["blockers"]))


if __name__ == "__main__": unittest.main()
