import unittest

from gacm.qualification import (
    DiscoveryObservation,
    EscapeScanResult,
    QualificationBlocked,
    QualificationCoordinator,
)


def node(node_id, req, invariant, prereq=(), retest=()):
    return {
        "node_id": node_id,
        "spec_requirement_id": req,
        "invariant": invariant,
        "affected_surface": ["app"],
        "prerequisites": list(prereq),
        "fixture_input": "fixture",
        "oracle": "oracle",
        "expected_result": "expected",
        "mutation_risk": "SANDBOX_ONLY",
        "failure_class": "PRODUCT_DIVERGENCE",
        "discovery_continuation_policy": "CONTINUE_SAFE_DISCOVERY",
        "repair_class": invariant,
        "transitive_retest_closure": list(retest),
        "required_evidence": ["receipt"],
        "final_verification_method": "INDEPENDENT_VERIFIER",
    }


class QualificationCoordinatorTests(unittest.TestCase):
    def make(self, discovery_fail=(), escape_nodes=(), regression=True, runtime=True):
        calls = {"discover": [], "repair": [], "retest": [], "final": []}
        nodes = [
            node("N1", "R1", "identity", retest=("N2",)),
            node("N2", "R2", "identity", prereq=("N1",), retest=("N3",)),
            node("N3", "R3", "presentation", prereq=("N2",)),
        ]

        def completeness(parsed):
            return {
                "status": "PASS",
                "issuer_role": "INDEPENDENT_VERIFIER",
                "authoritative": True,
                "spec_digest": "spec-1",
                "unmapped_requirements": [],
                "node_count": len(parsed),
                "verifier_id": "verifier-1",
                "evidence_id": "complete-1",
            }

        def discover(n):
            calls["discover"].append(n.node_id)
            return DiscoveryObservation(n.node_id, "FAIL" if n.node_id in discovery_fail else "PASS")

        def repair_plan(invariant, ids, state):
            return {"status": "PLANNED", "invariant": invariant, "ids": list(ids)}

        def repair_execute(invariant, ids, plan):
            calls["repair"].append((invariant, tuple(ids)))

        def retest(n):
            calls["retest"].append(n.node_id)
            return DiscoveryObservation(n.node_id, "PASS")

        def scan(graph, budget, state):
            invariants = tuple(sorted({next(n.invariant for n in graph.nodes if n.node_id == x) for x in escape_nodes}))
            return EscapeScanResult(budget, budget, invariants, tuple(escape_nodes))

        def final(n):
            calls["final"].append(n.node_id)
            return DiscoveryObservation(n.node_id, "PASS")

        def independent(state):
            graph = state["graph"]
            return {
                "status": "PASS",
                "authoritative": True,
                "issuer_role": "INDEPENDENT_VERIFIER",
                "graph_digest": graph["graph_digest"],
                "spec_digest": graph["spec_digest"],
            }

        coordinator = QualificationCoordinator(
            spec_digest="spec-1",
            normative_requirement_ids=("R1", "R2", "R3"),
            escape_scan_budget=3,
            compile_nodes=lambda: nodes,
            completeness_verify=completeness,
            discover_node=discover,
            repair_plan=repair_plan,
            repair_execute=repair_execute,
            retest_node=retest,
            escape_scan=scan,
            final_verify_node=final,
            full_regression=lambda state: regression,
            runtime_checks=lambda state: runtime,
            independent_final_verify=independent,
        )
        return coordinator, calls

    def test_complete_discovery_precedes_repair_and_clusters_invariant(self):
        c, calls = self.make(discovery_fail=("N1", "N2"))
        state = c.run()
        self.assertEqual(["N1", "N2", "N3"], calls["discover"])
        self.assertEqual([("identity", ("N1", "N2"))], calls["repair"])
        self.assertTrue(state["pre_promotion"]["ready"])

    def test_transitive_closure_retests_only_affected_graph_closure(self):
        c, calls = self.make(discovery_fail=("N1",))
        c.run()
        self.assertEqual(["N1", "N2", "N3"], calls["retest"])

    def test_unrelated_cluster_does_not_join_repair(self):
        c, calls = self.make(discovery_fail=("N3",))
        c.run()
        self.assertEqual([("presentation", ("N3",))], calls["repair"])
        self.assertEqual(["N3"], calls["retest"])

    def test_escape_defect_reopens_only_affected_closure(self):
        c, calls = self.make(escape_nodes=("N3",))
        state = c.run()
        self.assertIn(("presentation", ("N3",)), calls["repair"])
        self.assertEqual(["N3"], calls["retest"])
        self.assertEqual({"presentation": ["N3"]}, state["escaped_defect_closures"])

    def test_escape_budget_is_fixed(self):
        c, _ = self.make()
        c.escape_scan = lambda graph, budget, state: EscapeScanResult(budget + 1, budget + 1)
        with self.assertRaisesRegex(QualificationBlocked, "ESCAPE_SCAN_BUDGET_MUTATED"):
            c.run()

    def test_final_gate_blocks_bad_regression(self):
        c, _ = self.make(regression=False)
        with self.assertRaisesRegex(QualificationBlocked, "QUALIFICATION_PRE_PROMOTION_GATE_BLOCKED"):
            c.run()

    def test_final_gate_blocks_bad_runtime(self):
        c, _ = self.make(runtime=False)
        with self.assertRaisesRegex(QualificationBlocked, "QUALIFICATION_PRE_PROMOTION_GATE_BLOCKED"):
            c.run()

    def test_settle_is_required_for_final_termination(self):
        c, _ = self.make()
        state = c.run()
        not_done = c.finalize_after_settle(state, settle_succeeded=False)
        self.assertFalse(not_done["termination"]["complete"])
        done = c.finalize_after_settle(state, settle_succeeded=True)
        self.assertTrue(done["termination"]["complete"])

    def test_resume_rejects_changed_spec_digest(self):
        c, _ = self.make()
        state = c.run()
        other, _ = self.make()
        other.spec_digest = "changed"
        with self.assertRaisesRegex(QualificationBlocked, "QUALIFICATION_SPEC_DIGEST_CHANGED"):
            other.run(state)

    def test_denominator_mutation_fails_closed(self):
        c, _ = self.make()
        state = c.run()
        state["graph"]["denominator"] = 99
        with self.assertRaisesRegex(QualificationBlocked, "QUALIFICATION_DENOMINATOR_MUTATED"):
            c.run(state)

    def test_graph_digest_mutation_fails_closed(self):
        c, _ = self.make()
        state = c.run()
        state["graph"]["graph_digest"] = "0" * 64
        with self.assertRaisesRegex(QualificationBlocked, "QUALIFICATION_GRAPH_DIGEST_CHANGED"):
            c.run(state)


if __name__ == "__main__":
    unittest.main()
