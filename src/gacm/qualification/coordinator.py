"""Finite qualification lifecycle coordinator.

This is the authoritative qualification path used by the PilotHarness. It
separates discovery from mutation, clusters repair by invariant, enforces frozen
graph identity, bounds the escape scan, and produces a pre-promotion gate.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any, Callable, Iterable, Mapping

from .graph import (
    DiscoveryObservation,
    EscapeScanResult,
    QualificationGraph,
    QualificationGraphCompiler,
    QualificationNode,
    QualificationProgress,
    QualificationTermination,
)


class QualificationBlocked(RuntimeError):
    pass


class QualificationCoordinator:
    def __init__(
        self,
        *,
        spec_digest: str,
        normative_requirement_ids: Iterable[str],
        escape_scan_budget: int,
        compile_nodes: Callable[[], Iterable[Mapping[str, Any] | QualificationNode]],
        completeness_verify: Callable[[tuple[QualificationNode, ...]], Mapping[str, Any]],
        discover_node: Callable[[QualificationNode], DiscoveryObservation],
        repair_plan: Callable[[str, tuple[str, ...], Mapping[str, Any]], Mapping[str, Any]],
        repair_execute: Callable[[str, tuple[str, ...], Mapping[str, Any]], Any],
        retest_node: Callable[[QualificationNode], DiscoveryObservation],
        escape_scan: Callable[[QualificationGraph, int, Mapping[str, Any]], EscapeScanResult],
        final_verify_node: Callable[[QualificationNode], DiscoveryObservation],
        full_regression: Callable[[Mapping[str, Any]], bool],
        runtime_checks: Callable[[Mapping[str, Any]], bool],
        independent_final_verify: Callable[[Mapping[str, Any]], Mapping[str, Any]],
    ):
        self.spec_digest = str(spec_digest)
        self.requirement_ids = tuple(sorted(set(map(str, normative_requirement_ids))))
        self.escape_scan_budget = int(escape_scan_budget)
        self.compile_nodes = compile_nodes
        self.completeness_verify = completeness_verify
        self.discover_node = discover_node
        self.repair_plan = repair_plan
        self.repair_execute = repair_execute
        self.retest_node = retest_node
        self.escape_scan = escape_scan
        self.final_verify_node = final_verify_node
        self.full_regression = full_regression
        self.runtime_checks = runtime_checks
        self.independent_final_verify = independent_final_verify

    def run(self, durable_state: Mapping[str, Any] | None = None) -> dict[str, Any]:
        state = dict(durable_state or {})
        graph = self._graph_from_state(state)
        if graph is None:
            graph = self._compile_graph()
            state["graph"] = self._graph_snapshot(graph)
            state["normative_requirement_ids"] = list(self.requirement_ids)
            state["escape_scan_budget"] = self.escape_scan_budget
            state["progress"] = asdict(QualificationProgress.unavailable())
        self._assert_identity(graph, state)

        if "discovery_observations" not in state:
            observations = graph.discovery_sweep(self.discover_node)
            if observations and observations[-1].hard_stop:
                state["discovery_observations"] = [asdict(x) for x in observations]
                state["hard_stop_reason"] = observations[-1].failure_class or observations[-1].safety_class
                raise QualificationBlocked("QUALIFICATION_DISCOVERY_HARD_STOP")
            if len(observations) != graph.denominator:
                raise QualificationBlocked("QUALIFICATION_DISCOVERY_INCOMPLETE")
            state["discovery_observations"] = [asdict(x) for x in observations]

        discovery = tuple(DiscoveryObservation(**x) for x in state["discovery_observations"])
        clusters = graph.failure_clusters(discovery)
        state["discovered_defect_classes"] = sorted(clusters)
        closed = set(map(str, state.get("closed_defect_classes", ())))
        repair_receipts = list(state.get("repair_receipts", ()))

        for invariant, node_ids in clusters.items():
            if invariant in closed:
                continue
            plan = self.repair_plan(invariant, node_ids, state)
            if plan.get("status") != "PLANNED":
                raise QualificationBlocked("REPAIR_SCOPE_UNRESOLVED:" + invariant)
            self.repair_execute(invariant, node_ids, plan)
            closure = graph.retest_closure(node_ids)
            retests = []
            by_id = {node.node_id: node for node in graph.nodes}
            for node_id in closure:
                obs = self.retest_node(by_id[node_id])
                retests.append(asdict(obs))
                if obs.disposition not in ("PASS", "HUMAN_DEFERRED"):
                    raise QualificationBlocked("REPAIR_CLOSURE_UNRESOLVED:" + invariant)
            repair_receipts.append({
                "invariant": invariant,
                "nodes": list(node_ids),
                "closure": list(closure),
                "plan": dict(plan),
                "retests": retests,
            })
            closed.add(invariant)
        state["closed_defect_classes"] = sorted(closed)
        state["repair_receipts"] = repair_receipts

        if "escape_scan" not in state:
            scan = self.escape_scan(graph, self.escape_scan_budget, state)
            if scan.budget != self.escape_scan_budget:
                raise QualificationBlocked("ESCAPE_SCAN_BUDGET_MUTATED")
            state["escape_scan_original"] = asdict(scan)
            if scan.hard_stop_reason:
                state["escape_scan"] = asdict(scan)
                raise QualificationBlocked("ESCAPE_SCAN_HARD_STOP")
            if scan.escaped_defect_node_ids:
                self._close_escaped_defects(graph, scan, state)
                scan = EscapeScanResult(budget=scan.budget, executed=scan.executed)
            state["escape_scan"] = asdict(scan)

        scan = EscapeScanResult(**state["escape_scan"])
        final_observations = []
        for node in graph.nodes:
            obs = self.final_verify_node(node)
            final_observations.append(asdict(obs))
            if obs.disposition not in ("PASS", "HUMAN_DEFERRED"):
                raise QualificationBlocked("FINAL_GRAPH_QUALIFICATION_NOT_GREEN")
        state["final_observations"] = final_observations

        regression_green = bool(self.full_regression(state))
        runtime_green = bool(self.runtime_checks(state))
        final_receipt = dict(self.independent_final_verify(state))
        independent_green = (
            final_receipt.get("status") == "PASS"
            and final_receipt.get("authoritative") is True
            and final_receipt.get("issuer_role") == "INDEPENDENT_VERIFIER"
            and str(final_receipt.get("graph_digest", "")) == graph.graph_digest
            and str(final_receipt.get("spec_digest", "")) == graph.spec_digest
        )
        state["full_regression_green"] = regression_green
        state["runtime_checks_green"] = runtime_green
        state["independent_final_verification"] = final_receipt

        pre = QualificationTermination.evaluate_pre_promotion(
            graph,
            terminal_node_ids=[x["node_id"] for x in final_observations],
            discovered_defect_classes=state["discovered_defect_classes"],
            closed_or_human_deferred_defect_classes=state["closed_defect_classes"],
            escape_scan=scan,
            full_regression_green=regression_green,
            runtime_checks_green=runtime_green,
            independent_final_verification_green=independent_green,
        )
        state["pre_promotion"] = {"ready": pre.complete, "reasons": list(pre.reasons)}
        state["progress"] = asdict(QualificationProgress.from_frozen_graph(
            graph,
            discovery,
            state["closed_defect_classes"],
            state["discovered_defect_classes"],
            [x["node_id"] for x in final_observations],
        ))
        if not pre.complete:
            raise QualificationBlocked("QUALIFICATION_PRE_PROMOTION_GATE_BLOCKED:" + ",".join(pre.reasons))
        return state

    def finalize_after_settle(self, durable_state: Mapping[str, Any], *, settle_succeeded: bool) -> dict[str, Any]:
        state = dict(durable_state)
        graph = self._graph_from_state(state)
        if graph is None:
            raise QualificationBlocked("QUALIFICATION_GRAPH_MISSING_AT_SETTLE")
        if not state.get("pre_promotion", {}).get("ready"):
            raise QualificationBlocked("QUALIFICATION_PRE_PROMOTION_GATE_NOT_READY")
        scan = EscapeScanResult(**state["escape_scan"])
        final_receipt = state.get("independent_final_verification", {})
        result = QualificationTermination.evaluate(
            graph,
            terminal_node_ids=[x["node_id"] for x in state.get("final_observations", ())],
            discovered_defect_classes=state.get("discovered_defect_classes", ()),
            closed_or_human_deferred_defect_classes=state.get("closed_defect_classes", ()),
            escape_scan=scan,
            full_regression_green=bool(state.get("full_regression_green")),
            runtime_checks_green=bool(state.get("runtime_checks_green")),
            independent_final_verification_green=(
                final_receipt.get("status") == "PASS"
                and final_receipt.get("authoritative") is True
                and final_receipt.get("issuer_role") == "INDEPENDENT_VERIFIER"
            ),
            settle_succeeded=bool(settle_succeeded),
        )
        state["termination"] = {"complete": result.complete, "reasons": list(result.reasons)}
        return state

    def _compile_graph(self) -> QualificationGraph:
        nodes = tuple(
            item if isinstance(item, QualificationNode) else QualificationNode.from_mapping(item)
            for item in self.compile_nodes()
        )
        receipt = self.completeness_verify(nodes)
        return QualificationGraphCompiler.compile(
            spec_digest=self.spec_digest,
            normative_requirement_ids=self.requirement_ids,
            nodes=nodes,
            completeness_receipt=receipt,
        )

    def _close_escaped_defects(self, graph: QualificationGraph, scan: EscapeScanResult, state: dict[str, Any]) -> None:
        by_id = {node.node_id: node for node in graph.nodes}
        unknown = sorted(set(scan.escaped_defect_node_ids) - set(by_id))
        if unknown:
            raise QualificationBlocked("ESCAPE_SCAN_UNKNOWN_NODE:" + ",".join(unknown))
        groups: dict[str, list[str]] = {}
        for node_id in scan.escaped_defect_node_ids:
            groups.setdefault(by_id[node_id].invariant, []).append(node_id)
        original_groups = set(groups)
        if original_groups != set(scan.escaped_defect_invariants):
            raise QualificationBlocked("ESCAPE_SCAN_INVARIANT_NODE_MISMATCH")
        closures = {}
        for invariant, node_ids in sorted(groups.items()):
            ids = tuple(sorted(node_ids))
            plan = self.repair_plan(invariant, ids, state)
            if plan.get("status") != "PLANNED":
                raise QualificationBlocked("ESCAPED_REPAIR_SCOPE_UNRESOLVED:" + invariant)
            self.repair_execute(invariant, ids, plan)
            closure = graph.retest_closure(ids)
            closures[invariant] = list(closure)
            for node_id in closure:
                obs = self.retest_node(by_id[node_id])
                if obs.disposition not in ("PASS", "HUMAN_DEFERRED"):
                    raise QualificationBlocked("ESCAPED_DEFECT_CLOSURE_UNRESOLVED:" + invariant)
        state["escaped_defect_closures"] = closures

    @staticmethod
    def _graph_snapshot(graph: QualificationGraph) -> dict[str, Any]:
        return {
            "spec_digest": graph.spec_digest,
            "graph_digest": graph.graph_digest,
            "denominator": graph.denominator,
            "completeness_verifier": graph.completeness_verifier,
            "completeness_evidence": graph.completeness_evidence,
            "completeness_receipt_digest": graph.completeness_receipt_digest,
            "nodes": [node.to_dict() for node in graph.nodes],
            "frozen": True,
        }

    @staticmethod
    def _graph_from_state(state: Mapping[str, Any]) -> QualificationGraph | None:
        raw = state.get("graph")
        if not raw:
            return None
        nodes = tuple(QualificationNode.from_mapping(x) for x in raw["nodes"])
        return QualificationGraph(
            spec_digest=str(raw["spec_digest"]),
            nodes=nodes,
            graph_digest=str(raw["graph_digest"]),
            completeness_verifier=str(raw["completeness_verifier"]),
            completeness_evidence=str(raw["completeness_evidence"]),
            completeness_receipt_digest=str(raw["completeness_receipt_digest"]),
            frozen=True,
        )

    def _assert_identity(self, graph: QualificationGraph, state: Mapping[str, Any]) -> None:
        if graph.spec_digest != self.spec_digest:
            raise QualificationBlocked("QUALIFICATION_SPEC_DIGEST_CHANGED")
        persisted_requirements = tuple(sorted(map(str, state.get("normative_requirement_ids", self.requirement_ids))))
        if persisted_requirements != tuple(sorted(self.requirement_ids)):
            raise QualificationBlocked("QUALIFICATION_REQUIREMENT_SET_CHANGED")
        if int(state.get("escape_scan_budget", self.escape_scan_budget)) != self.escape_scan_budget:
            raise QualificationBlocked("ESCAPE_SCAN_BUDGET_MUTATED")
        if graph.denominator != len(graph.nodes):
            raise QualificationBlocked("QUALIFICATION_DENOMINATOR_MUTATED")
        raw = state.get("graph", {})
        if raw and int(raw.get("denominator", -1)) != graph.denominator:
            raise QualificationBlocked("QUALIFICATION_DENOMINATOR_MUTATED")
        material = {
            "spec_digest": graph.spec_digest,
            "requirements": tuple(sorted(self.requirement_ids)),
            "nodes": [node.to_dict() for node in sorted(graph.nodes, key=lambda item: item.node_id)],
            "completeness_verifier": graph.completeness_verifier,
            "completeness_evidence": graph.completeness_evidence,
            "completeness_receipt_digest": graph.completeness_receipt_digest,
        }
        expected = hashlib.sha256(
            json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str).encode()
        ).hexdigest()
        if expected != graph.graph_digest:
            raise QualificationBlocked("QUALIFICATION_GRAPH_DIGEST_CHANGED")
