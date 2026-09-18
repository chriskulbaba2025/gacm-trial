import unittest

from gacm.qualification import (
    DiscoveryObservation,
    EscapeScanResult,
    QualificationGraphCompiler,
    QualificationProgress,
    QualificationTermination,
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


class QualificationGraphTests(unittest.TestCase):
    def compile(self):
        return QualificationGraphCompiler.compile(
            spec_digest="c506",
            normative_requirement_ids=["R1", "R2", "R3"],
            nodes=[
                node("N1", "R1", "identity", retest=("N2",)),
                node("N2", "R2", "identity", prereq=("N1",), retest=("N3",)),
                node("N3", "R3", "presentation", prereq=("N2",)),
            ],
            completeness_verifier="independent-verifier",
            completeness_evidence="proof-1",
        )

    def test_freeze_requires_zero_unmapped_requirements(self):
        with self.assertRaisesRegex(ValueError, "UNMAPPED_SPEC_REQUIREMENTS"):
            QualificationGraphCompiler.compile(
                spec_digest="x",
                normative_requirement_ids=["R1", "R2"],
                nodes=[node("N1", "R1", "identity")],
                completeness_verifier="verifier",
                completeness_evidence="proof",
            )

    def test_foreign_node_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "QUALIFICATION_NODE_WITHOUT_SPEC_REQUIREMENT"):
            QualificationGraphCompiler.compile(
                spec_digest="x",
                normative_requirement_ids=["R1"],
                nodes=[node("N1", "R1", "identity"), node("N2", "R2", "identity")],
                completeness_verifier="verifier",
                completeness_evidence="proof",
            )

    def test_discovery_continues_after_ordinary_failures(self):
        graph = self.compile()
        seen = []
        def execute(n):
            seen.append(n.node_id)
            return DiscoveryObservation(n.node_id, "FAIL" if n.node_id == "N1" else "PASS")
        observations = graph.discovery_sweep(execute)
        self.assertEqual([x.node_id for x in observations], ["N1", "N2", "N3"])
        self.assertEqual(seen, ["N1", "N2", "N3"])

    def test_hard_stop_stops_safe_discovery(self):
        graph = self.compile()
        def execute(n):
            if n.node_id == "N2":
                return DiscoveryObservation(n.node_id, "BLOCKED", "PRODUCTION_ACCESS")
            return DiscoveryObservation(n.node_id, "PASS")
        observations = graph.discovery_sweep(execute)
        self.assertEqual([x.node_id for x in observations], ["N1", "N2"])

    def test_failures_cluster_by_invariant_not_test_row(self):
        graph = self.compile()
        observations = (
            DiscoveryObservation("N1", "FAIL"),
            DiscoveryObservation("N2", "FAIL"),
            DiscoveryObservation("N3", "FAIL"),
        )
        self.assertEqual(graph.failure_clusters(observations), {
            "identity": ("N1", "N2"),
            "presentation": ("N3",),
        })

    def test_retest_closure_is_transitive(self):
        self.assertEqual(self.compile().retest_closure(["N1"]), ("N1", "N2", "N3"))

    def test_progress_is_unavailable_before_freeze(self):
        progress = QualificationProgress.unavailable()
        self.assertEqual(progress.discovery_coverage, "UNAVAILABLE")
        self.assertIsNone(progress.denominator)

    def test_escape_scan_budget_cannot_self_extend(self):
        with self.assertRaisesRegex(ValueError, "INVALID_ESCAPE_SCAN_BUDGET"):
            EscapeScanResult(budget=5, executed=6)

    def test_termination_is_explicit_and_finite(self):
        graph = self.compile()
        result = QualificationTermination.evaluate(
            graph,
            terminal_node_ids=["N1", "N2", "N3"],
            discovered_defect_classes=["identity"],
            closed_or_human_deferred_defect_classes=["identity"],
            escape_scan=EscapeScanResult(budget=3, executed=3),
            full_regression_green=True,
            runtime_checks_green=True,
            independent_final_verification_green=True,
            settle_succeeded=True,
        )
        self.assertTrue(result.complete)
        self.assertEqual(result.reasons, ())


if __name__ == "__main__":
    unittest.main()
