import unittest

from gacm.harness import HarnessAdapters, HarnessConfig, MemoryRunStateStore, PilotHarness, TopLevelState
from gacm.qualification import DiscoveryObservation, EscapeScanResult


SHA = "a" * 40


def config(**kwargs):
    values = dict(
        project_id="synthetic",
        prd_identity="prd-v1",
        authoritative_start_sha=SHA,
        branch_or_worktree="isolated",
        gacm_version="4.2.2",
        execution_policy={},
        human_authority={"promotion_required": False},
        discovery_config={},
        operational_context_requirements={},
        frozen_spec_digest="spec-1",
        normative_requirement_ids=("R1", "R2"),
        escape_scan_budget=2,
    )
    values.update(kwargs)
    return HarnessConfig(**values)


def qnode(node_id, req, invariant):
    return {
        "node_id": node_id,
        "spec_requirement_id": req,
        "invariant": invariant,
        "affected_surface": ["app"],
        "prerequisites": [],
        "fixture_input": "fixture",
        "oracle": "oracle",
        "expected_result": "expected",
        "mutation_risk": "SANDBOX_ONLY",
        "failure_class": "PRODUCT_DIVERGENCE",
        "discovery_continuation_policy": "CONTINUE_SAFE_DISCOVERY",
        "repair_class": invariant,
        "transitive_retest_closure": [],
        "required_evidence": ["receipt"],
        "final_verification_method": "INDEPENDENT_VERIFIER",
    }


class PilotHarnessTests(unittest.TestCase):
    def make(self, fail_node=None, settle_outcome="PASS", authority="VERIFIED", context="VERIFIED"):
        store = MemoryRunStateStore()
        calls = {"discover": [], "repair": [], "promotion": 0}

        def completeness(c, nodes):
            return {
                "status": "PASS", "issuer_role": "INDEPENDENT_VERIFIER", "authoritative": True,
                "spec_digest": c.frozen_spec_digest, "unmapped_requirements": [],
                "node_count": len(nodes), "verifier_id": "iv", "evidence_id": "proof",
            }

        def discover(n, ctx):
            calls["discover"].append(n.node_id)
            return DiscoveryObservation(n.node_id, "FAIL" if n.node_id == fail_node else "PASS")

        def repair(invariant, ids, plan, ctx):
            calls["repair"].append((invariant, tuple(ids)))
            return {"status": "COMPLETED"}

        def final_verify(state, ctx):
            g = state["graph"]
            return {
                "status": "PASS", "authoritative": True, "issuer_role": "INDEPENDENT_VERIFIER",
                "graph_digest": g["graph_digest"], "spec_digest": g["spec_digest"],
            }

        def promotion(s, h):
            calls["promotion"] += 1
            return {"state": "SETTLE_REQUIRED"}

        def settle(s, p):
            return {"status": "SETTLE_PASS" if settle_outcome == "PASS" else "SETTLE_FAIL"}

        def current_identity(c):
            if not store.states:
                return {}
            raw = next(iter(store.states.values())).get("qualification", {}).get("graph", {})
            return {
                "spec_digest": raw.get("spec_digest"),
                "graph_digest": raw.get("graph_digest"),
                "denominator": raw.get("denominator"),
            }

        adapters = HarnessAdapters(
            authority=lambda c: {"status": authority, "sha": SHA},
            discovery=lambda c, a: {"status": "DISCOVERED"},
            context=lambda c, a, d: {"status": context, "context_id": "ctx-1"},
            plan=lambda c, x, w: [{"unit_id": "u1"}, {"unit_id": "u2"}],
            qualification_nodes=lambda c, x, units: [qnode("N1", "R1", "identity"), qnode("N2", "R2", "presentation")],
            qualification_completeness=completeness,
            qualification_discover=discover,
            qualification_repair_plan=lambda inv, ids, s: {"status": "PLANNED"},
            qualification_repair=repair,
            qualification_retest=lambda n, ctx: DiscoveryObservation(n.node_id, "PASS"),
            qualification_escape_scan=lambda g, b, s, ctx: EscapeScanResult(b, b),
            qualification_final_verify_node=lambda n, ctx: DiscoveryObservation(n.node_id, "PASS"),
            qualification_full_regression=lambda s, ctx: True,
            qualification_runtime_checks=lambda s, ctx: True,
            qualification_independent_final_verify=final_verify,
            promotion=promotion,
            settle=settle,
            rollback=lambda s, r: {"state": "ROLLED_BACK"},
            current_authority=lambda c: SHA,
            current_qualification_identity=current_identity,
        )
        return PilotHarness(adapters, store), config(), calls, store

    def test_clean_pass_and_resume_is_durable(self):
        h, c, calls, store = self.make()
        result = h.run(c, [{"unit_id": "u1"}])
        self.assertEqual(result["state"], TopLevelState.COMPLETED.value)
        self.assertTrue(result["qualification"]["termination"]["complete"])
        again = h.run(c, run_id=result["run_id"], resume=True)
        self.assertEqual(again, result)

    def test_discovery_finishes_before_clustered_repair(self):
        h, c, calls, _ = self.make(fail_node="N1")
        result = h.run(c)
        self.assertEqual(["N1", "N2"], calls["discover"])
        self.assertEqual([("identity", ("N1",))], calls["repair"])
        self.assertEqual(result["state"], "COMPLETED")

    def test_authority_block_prevents_qualification(self):
        h, c, calls, _ = self.make(authority="AMBIGUOUS")
        result = h.run(c)
        self.assertEqual(result["state"], "BLOCKED")
        self.assertEqual([], calls["discover"])

    def test_promotion_requires_finite_qualification(self):
        h, c, calls, _ = self.make()
        original = h.adapters.qualification_full_regression
        object.__setattr__(h.adapters, "qualification_full_regression", lambda s, ctx: False)
        result = h.run(c)
        self.assertEqual(result["state"], "BLOCKED")
        self.assertEqual(0, calls["promotion"])
        object.__setattr__(h.adapters, "qualification_full_regression", original)

    def test_settle_failure_requires_rollback(self):
        h, c, _, _ = self.make(settle_outcome="FAIL")
        result = h.run(c)
        self.assertEqual(result["state"], "ROLLBACK_REQUIRED")
        self.assertFalse(result["qualification"]["termination"]["complete"])
        self.assertTrue(result["receipts"]["rollback"])

    def test_human_gate(self):
        h, c, _, _ = self.make()
        c = config(human_authority={"promotion_required": True})
        paused = h.run(c)
        self.assertEqual(paused["state"], "PROMOTION_PENDING")
        done = h.run(c, run_id=paused["run_id"], resume=True, human_approval=True)
        self.assertEqual(done["state"], "COMPLETED")

    def test_resume_rejects_graph_identity_change(self):
        h, c, _, store = self.make()
        result = h.run(c)
        raw = store.states[result["run_id"]]
        raw["state"] = "PROMOTION_PENDING"
        raw["qualification"]["graph"]["graph_digest"] = "tampered"
        resumed = h.run(c, run_id=result["run_id"], resume=True, human_approval=True)
        self.assertEqual(resumed["state"], "BLOCKED")
        self.assertIn("QUALIFICATION_GRAPH_DIGEST_CHANGED", resumed["blockers"])


if __name__ == "__main__":
    unittest.main()
