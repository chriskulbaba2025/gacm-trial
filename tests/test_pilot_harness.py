import unittest

from gacm.harness import HarnessAdapters, HarnessConfig, MemoryRunStateStore, PilotHarness, TopLevelState


SHA = "a" * 40


def config(**kwargs):
    values = dict(project_id="synthetic", prd_identity="prd-v1", authoritative_start_sha=SHA,
                  branch_or_worktree="isolated", gacm_version="4.2.2", execution_policy={},
                  human_authority={"promotion_required": False}, discovery_config={},
                  operational_context_requirements={})
    values.update(kwargs)
    return HarnessConfig(**values)


class PilotHarnessTests(unittest.TestCase):
    def make(self, verify_status="PASS", settle_outcome="PASS", authority="VERIFIED", context="VERIFIED", route=True, broad=False):
        store = MemoryRunStateStore(); calls = {"execute": 0, "verify": 0}
        def authority_fn(c): return {"status": authority, "sha": SHA}
        def context_fn(c, a, d): return {"status": context, "context_id": "ctx-1"}
        def route_fn(u): return {"selected_model": "Luna", "qualification_identity": "qual-1"} if route else {"selected_model": "Luna"}
        def execute(u, r, c): calls["execute"] += 1; return {"execution_status": "COMPLETED", "ending_sha": SHA}
        def verify(u, e, c): calls["verify"] += 1; return {"status": verify_status if calls["verify"] == 1 else "PASS", "issuer_role": "INDEPENDENT_VERIFIER"}
        def repair_plan(u, v, s): return {"status": "PLANNED", "classification": "BROADER_REQUALIFICATION" if broad else "LOCAL"}
        def repair(u, p, c): return {"execution_status": "COMPLETED", "ending_sha": SHA}
        def identity(u, c): return {"result": "VALID"}
        def promotion(s, h): return {"state": "SETTLE_REQUIRED"}
        def settle(s, p): return {"status": "SETTLE_PASS" if settle_outcome == "PASS" else "SETTLE_FAIL"}
        def rollback(s, r): return {"state": "ROLLED_BACK"}
        adapters = HarnessAdapters(authority_fn, lambda c, a: {"status": "DISCOVERED"}, context_fn,
                                   lambda c, x, w: [{"unit_id": "u1", "title": "unit", "status": "PENDING"}],
                                   route_fn, execute, verify, repair_plan, repair, identity_validate=identity, promotion=promotion,
                                   settle=settle, rollback=rollback)
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

    def test_human_gate(self):
        h, c, _, _ = self.make(); c = config(human_authority={"promotion_required": True})
        paused = h.run(c, [{"unit_id": "u1"}]); self.assertEqual(paused["state"], "PROMOTION_PENDING")
        done = h.run(c, run_id=paused["run_id"], resume=True, human_approval=True)
        self.assertEqual(done["state"], "COMPLETED")


if __name__ == "__main__": unittest.main()
