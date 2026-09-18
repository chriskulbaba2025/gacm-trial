"""Finite qualification graph and batch-discovery controls for GACM.

This module deliberately separates qualification discovery from mutation. A frozen
graph establishes the denominator; a discovery sweep records all sandbox-safe
outcomes without repairing; repair planning operates on invariant classes and
transitive dependency closure; the escape scan has a fixed budget; termination is
explicit and machine-checkable.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Callable, Iterable, Mapping, Sequence


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)


class NodeDisposition(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    HUMAN_DEFERRED = "HUMAN_DEFERRED"


class FailureSafety(StrEnum):
    ORDINARY_PRODUCT_DIVERGENCE = "ORDINARY_PRODUCT_DIVERGENCE"
    HARD_STOP = "HARD_STOP"


HARD_STOP_CLASSES = {
    "AUTHORITY_VIOLATION",
    "UNEXPECTED_EXTERNAL_MUTATION",
    "PRODUCTION_ACCESS",
    "DESTRUCTIVE_CORRUPTION",
    "CREDENTIAL_EXPOSURE",
    "SECURITY_EXPOSURE",
    "VERIFIER_COMPROMISE",
    "UNSAFE_EXECUTION",
}


@dataclass(frozen=True)
class QualificationNode:
    node_id: str
    spec_requirement_id: str
    invariant: str
    affected_surface: tuple[str, ...]
    prerequisites: tuple[str, ...]
    fixture_input: str
    oracle: str
    expected_result: str
    mutation_risk: str
    failure_class: str
    discovery_continuation_policy: str
    repair_class: str
    transitive_retest_closure: tuple[str, ...]
    required_evidence: tuple[str, ...]
    final_verification_method: str

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "QualificationNode":
        required = (
            "node_id", "spec_requirement_id", "invariant", "affected_surface",
            "prerequisites", "fixture_input", "oracle", "expected_result",
            "mutation_risk", "failure_class", "discovery_continuation_policy",
            "repair_class", "transitive_retest_closure", "required_evidence",
            "final_verification_method",
        )
        missing = [key for key in required if key not in raw]
        if missing:
            raise ValueError("QUALIFICATION_NODE_MISSING_FIELDS:" + ",".join(sorted(missing)))
        return cls(
            node_id=str(raw["node_id"]),
            spec_requirement_id=str(raw["spec_requirement_id"]),
            invariant=str(raw["invariant"]),
            affected_surface=tuple(map(str, raw["affected_surface"])),
            prerequisites=tuple(map(str, raw["prerequisites"])),
            fixture_input=str(raw["fixture_input"]),
            oracle=str(raw["oracle"]),
            expected_result=str(raw["expected_result"]),
            mutation_risk=str(raw["mutation_risk"]),
            failure_class=str(raw["failure_class"]),
            discovery_continuation_policy=str(raw["discovery_continuation_policy"]),
            repair_class=str(raw["repair_class"]),
            transitive_retest_closure=tuple(map(str, raw["transitive_retest_closure"])),
            required_evidence=tuple(map(str, raw["required_evidence"])),
            final_verification_method=str(raw["final_verification_method"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "spec_requirement_id": self.spec_requirement_id,
            "invariant": self.invariant,
            "affected_surface": list(self.affected_surface),
            "prerequisites": list(self.prerequisites),
            "fixture_input": self.fixture_input,
            "oracle": self.oracle,
            "expected_result": self.expected_result,
            "mutation_risk": self.mutation_risk,
            "failure_class": self.failure_class,
            "discovery_continuation_policy": self.discovery_continuation_policy,
            "repair_class": self.repair_class,
            "transitive_retest_closure": list(self.transitive_retest_closure),
            "required_evidence": list(self.required_evidence),
            "final_verification_method": self.final_verification_method,
        }


@dataclass(frozen=True)
class DiscoveryObservation:
    node_id: str
    disposition: str
    failure_class: str | None = None
    evidence: tuple[str, ...] = ()
    safety_class: str = FailureSafety.ORDINARY_PRODUCT_DIVERGENCE.value

    @property
    def hard_stop(self) -> bool:
        return self.safety_class == FailureSafety.HARD_STOP.value or (
            self.failure_class in HARD_STOP_CLASSES if self.failure_class else False
        )


@dataclass(frozen=True)
class QualificationGraph:
    spec_digest: str
    nodes: tuple[QualificationNode, ...]
    graph_digest: str
    completeness_verifier: str
    completeness_evidence: str
    completeness_receipt_digest: str
    frozen: bool = True

    @property
    def denominator(self) -> int:
        return len(self.nodes)

    def node_ids(self) -> tuple[str, ...]:
        return tuple(node.node_id for node in self.nodes)

    def discovery_sweep(
        self,
        execute_node: Callable[[QualificationNode], DiscoveryObservation],
    ) -> tuple[DiscoveryObservation, ...]:
        """Run all safe nodes without mutation/repair.

        Ordinary FAIL/BLOCKED observations are recorded and discovery continues.
        Only an unsafe condition stops the sweep.
        """
        observations: list[DiscoveryObservation] = []
        terminal = {NodeDisposition.PASS.value, NodeDisposition.FAIL.value, NodeDisposition.BLOCKED.value, NodeDisposition.HUMAN_DEFERRED.value}
        for node in self.nodes:
            obs = execute_node(node)
            if obs.node_id != node.node_id:
                raise ValueError("DISCOVERY_NODE_IDENTITY_MISMATCH")
            if obs.disposition not in terminal:
                raise ValueError("NON_TERMINAL_DISCOVERY_DISPOSITION")
            observations.append(obs)
            if obs.hard_stop:
                break
        return tuple(observations)

    def failure_clusters(self, observations: Iterable[DiscoveryObservation]) -> dict[str, tuple[str, ...]]:
        clusters: dict[str, list[str]] = {}
        by_id = {node.node_id: node for node in self.nodes}
        for obs in observations:
            if obs.disposition != NodeDisposition.FAIL.value:
                continue
            node = by_id[obs.node_id]
            key = node.invariant
            clusters.setdefault(key, []).append(node.node_id)
        return {key: tuple(sorted(value)) for key, value in sorted(clusters.items())}

    def retest_closure(self, repaired_node_ids: Iterable[str]) -> tuple[str, ...]:
        """Return the deterministic transitive retest closure for a bounded repair."""
        by_id = {node.node_id: node for node in self.nodes}
        closure = set(map(str, repaired_node_ids))
        pending = list(closure)
        while pending:
            current = pending.pop()
            node = by_id.get(current)
            if not node:
                raise ValueError("UNKNOWN_QUALIFICATION_NODE:" + current)
            for dependent in node.transitive_retest_closure:
                if dependent not in by_id:
                    raise ValueError("INVALID_RETEST_CLOSURE_REFERENCE:" + dependent)
                if dependent not in closure:
                    closure.add(dependent)
                    pending.append(dependent)
        return tuple(sorted(closure))


@dataclass(frozen=True)
class QualificationProgress:
    graph_frozen: bool
    denominator: int | None
    discovery_coverage: str
    defect_closure: str
    final_qualification_coverage: str

    @classmethod
    def unavailable(cls) -> "QualificationProgress":
        return cls(False, None, "UNAVAILABLE", "UNAVAILABLE", "UNAVAILABLE")

    @classmethod
    def from_frozen_graph(
        cls,
        graph: QualificationGraph,
        observations: Sequence[DiscoveryObservation],
        closed_defect_classes: Iterable[str],
        all_defect_classes: Iterable[str],
        final_terminal_nodes: Iterable[str],
    ) -> "QualificationProgress":
        observed = len({o.node_id for o in observations})
        total = graph.denominator
        all_classes = set(map(str, all_defect_classes))
        closed = set(map(str, closed_defect_classes))
        final = len(set(map(str, final_terminal_nodes)))
        pct = lambda n: f"{(100.0 * n / total):.1f}%" if total else "100.0%"
        defect = "100.0%" if not all_classes else f"{(100.0 * len(closed & all_classes) / len(all_classes)):.1f}%"
        return cls(True, total, pct(observed), defect, pct(final))


@dataclass(frozen=True)
class EscapeScanResult:
    budget: int
    executed: int
    escaped_defect_invariants: tuple[str, ...] = ()
    escaped_defect_node_ids: tuple[str, ...] = ()
    hard_stop_reason: str | None = None

    def __post_init__(self):
        if self.budget < 0 or self.executed < 0 or self.executed > self.budget:
            raise ValueError("INVALID_ESCAPE_SCAN_BUDGET")
        if bool(self.escaped_defect_invariants) != bool(self.escaped_defect_node_ids):
            raise ValueError("ESCAPED_DEFECT_IDENTITY_INCOMPLETE")

    @property
    def complete(self) -> bool:
        return self.hard_stop_reason is None and self.executed == self.budget


@dataclass(frozen=True)
class QualificationTermination:
    complete: bool
    reasons: tuple[str, ...]

    @classmethod
    def evaluate_pre_promotion(
        cls,
        graph: QualificationGraph,
        terminal_node_ids: Iterable[str],
        discovered_defect_classes: Iterable[str],
        closed_or_human_deferred_defect_classes: Iterable[str],
        escape_scan: EscapeScanResult,
        *,
        full_regression_green: bool,
        runtime_checks_green: bool,
        independent_final_verification_green: bool,
    ) -> "QualificationTermination":
        result = cls.evaluate(
            graph,
            terminal_node_ids,
            discovered_defect_classes,
            closed_or_human_deferred_defect_classes,
            escape_scan,
            full_regression_green=full_regression_green,
            runtime_checks_green=runtime_checks_green,
            independent_final_verification_green=independent_final_verification_green,
            settle_succeeded=True,
        )
        return cls(
            not result.reasons,
            tuple(reason for reason in result.reasons if reason != "SETTLE_NOT_SUCCEEDED"),
        )

    @classmethod
    def evaluate(
        cls,
        graph: QualificationGraph,
        terminal_node_ids: Iterable[str],
        discovered_defect_classes: Iterable[str],
        closed_or_human_deferred_defect_classes: Iterable[str],
        escape_scan: EscapeScanResult,
        *,
        full_regression_green: bool,
        runtime_checks_green: bool,
        independent_final_verification_green: bool,
        settle_succeeded: bool,
    ) -> "QualificationTermination":
        reasons: list[str] = []
        terminal = set(map(str, terminal_node_ids))
        expected = set(graph.node_ids())
        if terminal != expected:
            reasons.append("NON_TERMINAL_GRAPH_NODES")
        discovered = set(map(str, discovered_defect_classes))
        closed = set(map(str, closed_or_human_deferred_defect_classes))
        if not discovered.issubset(closed):
            reasons.append("OPEN_DEFECT_CLASSES")
        if not escape_scan.complete:
            reasons.append("ESCAPE_SCAN_INCOMPLETE")
        if escape_scan.escaped_defect_invariants:
            reasons.append("ESCAPED_DEFECT_REQUIRES_AFFECTED_CLOSURE")
        if not full_regression_green:
            reasons.append("FULL_REGRESSION_NOT_GREEN")
        if not runtime_checks_green:
            reasons.append("RUNTIME_CHECKS_NOT_GREEN")
        if not independent_final_verification_green:
            reasons.append("INDEPENDENT_FINAL_VERIFICATION_NOT_GREEN")
        if not settle_succeeded:
            reasons.append("SETTLE_NOT_SUCCEEDED")
        return cls(not reasons, tuple(reasons))


class QualificationGraphCompiler:
    """Compile and freeze a finite graph from a frozen SPEC requirement set."""

    @staticmethod
    def compile(
        *,
        spec_digest: str,
        normative_requirement_ids: Iterable[str],
        nodes: Iterable[Mapping[str, Any] | QualificationNode],
        completeness_receipt: Mapping[str, Any],
    ) -> QualificationGraph:
        requirements = tuple(sorted(set(map(str, normative_requirement_ids))))
        if not requirements:
            raise ValueError("EMPTY_NORMATIVE_REQUIREMENT_SET")
        parsed = tuple(
            node if isinstance(node, QualificationNode) else QualificationNode.from_mapping(node)
            for node in nodes
        )
        if not parsed:
            raise ValueError("EMPTY_QUALIFICATION_GRAPH")
        ids = [node.node_id for node in parsed]
        if len(ids) != len(set(ids)):
            raise ValueError("DUPLICATE_QUALIFICATION_NODE_ID")
        mapped = {node.spec_requirement_id for node in parsed}
        required = set(requirements)
        unmapped = sorted(required - mapped)
        foreign = sorted(mapped - required)
        if unmapped:
            raise ValueError("UNMAPPED_SPEC_REQUIREMENTS:" + ",".join(unmapped))
        if foreign:
            raise ValueError("QUALIFICATION_NODE_WITHOUT_SPEC_REQUIREMENT:" + ",".join(foreign))
        known = set(ids)
        for node in parsed:
            invalid_prereqs = sorted(set(node.prerequisites) - known)
            invalid_retests = sorted(set(node.transitive_retest_closure) - known)
            if invalid_prereqs:
                raise ValueError("UNKNOWN_PREREQUISITE:" + ",".join(invalid_prereqs))
            if invalid_retests:
                raise ValueError("UNKNOWN_RETEST_NODE:" + ",".join(invalid_retests))
        receipt = dict(completeness_receipt)
        if receipt.get("status") != "PASS" or receipt.get("issuer_role") != "INDEPENDENT_VERIFIER":
            raise ValueError("INDEPENDENT_COMPLETENESS_VERIFICATION_REQUIRED")
        if receipt.get("authoritative") is not True:
            raise ValueError("COMPLETENESS_VERIFICATION_NOT_AUTHORITATIVE")
        if str(receipt.get("spec_digest", "")) != str(spec_digest):
            raise ValueError("COMPLETENESS_SPEC_DIGEST_MISMATCH")
        if list(receipt.get("unmapped_requirements", [])):
            raise ValueError("COMPLETENESS_RECEIPT_HAS_UNMAPPED_REQUIREMENTS")
        if int(receipt.get("node_count", -1)) != len(parsed):
            raise ValueError("COMPLETENESS_NODE_COUNT_MISMATCH")
        completeness_verifier = str(receipt.get("verifier_id", ""))
        completeness_evidence = str(receipt.get("evidence_id", ""))
        if not completeness_verifier or not completeness_evidence:
            raise ValueError("COMPLETENESS_RECEIPT_IDENTITY_MISSING")
        completeness_receipt_digest = hashlib.sha256(_canonical(receipt).encode()).hexdigest()
        material = {
            "spec_digest": spec_digest,
            "requirements": requirements,
            "nodes": [node.to_dict() for node in sorted(parsed, key=lambda item: item.node_id)],
            "completeness_verifier": completeness_verifier,
            "completeness_evidence": completeness_evidence,
            "completeness_receipt_digest": completeness_receipt_digest,
        }
        digest = hashlib.sha256(_canonical(material).encode()).hexdigest()
        return QualificationGraph(
            spec_digest=str(spec_digest),
            nodes=tuple(sorted(parsed, key=lambda item: item.node_id)),
            graph_digest=digest,
            completeness_verifier=str(completeness_verifier),
            completeness_evidence=str(completeness_evidence),
            completeness_receipt_digest=completeness_receipt_digest,
            frozen=True,
        )
