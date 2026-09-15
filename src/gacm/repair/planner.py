"""Deterministic Repair-Scope / Dependency Engine (Phase 9)."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Callable, Iterable, Mapping

from .dependencies import WorkUnitDependencyGraph, surface_flag
from .invalidation import invalidate, normalize_assurance
from .models import BLOCKED_FOR_SCOPE_RESOLUTION, RepairClassification, RepairPlan, _canonical


class RepairScopePlanner:
    """Calculate the smallest proven re-verification scope.

    Executor claims are intentionally not accepted as classification input.
    ``verification_receipt`` is the only classification observation accepted
    from the verifier boundary, and it is cross-checked against raw evidence.
    """

    def __init__(self, clock: Callable[[], str] | None = None):
        self.clock = clock or (lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    def plan(self, verification_receipt: Mapping[str, Any] | Any, *, repair_scope_classification: str | None = None,
             actual_changed_paths: Iterable[str] | None = None, dependency_evidence: Iterable[Any] = (),
             work_units: Iterable[Mapping[str, Any]] = (), prior_pass_receipts: Iterable[Any] = (),
             surface_flags: Mapping[str, Any] | None = None, broader_requalification_triggers: Iterable[str] = (),
             graphify_discovery: Iterable[Any] = (), git_relationships: Iterable[Any] = (),
             source_work_unit_id: str | None = None, run_id: str | None = None) -> RepairPlan:
        receipt = verification_receipt if isinstance(verification_receipt, Mapping) else vars(verification_receipt)
        scope = receipt.get("affected_scope_determination", {})
        paths = None if actual_changed_paths is None else tuple(sorted(set(map(str, actual_changed_paths))))
        units = tuple(work_units)
        source = source_work_unit_id or str(receipt.get("work_unit_id", ""))
        run = run_id or str(receipt.get("run_id", ""))
        evidence = list(dependency_evidence) + list(git_relationships)
        graph = WorkUnitDependencyGraph(units, evidence)
        flags = surface_flags or {}
        patterns = {k: tuple(v) for k, v in flags.items() if isinstance(v, (tuple, list, set))}
        if paths is None:
            classification = RepairClassification.UNKNOWN.value
            direct, transitive = (), ()
            reasons = ["NO_INDEPENDENT_CHANGED_PATH_OBSERVATION"]
        else:
            explicit_flags = {k: bool(v) for k, v in flags.items() if isinstance(v, bool)}
            authority = surface_flag(paths, patterns.get("authority", ()), explicit_flags.get("authority", False))
            model = surface_flag(paths, patterns.get("model", ()), explicit_flags.get("model", False))
            architecture = surface_flag(paths, patterns.get("architecture", ()), explicit_flags.get("architecture", False))
            dependency = surface_flag(paths, patterns.get("dependency", ()), explicit_flags.get("dependency", False))
            direct = graph.units_for_paths(paths) or ((source,) if source else ())
            transitive = graph.transitive_dependents(direct)
            if authority: classification, reasons = "AUTHORITY_BEARING", ["SHARED_AUTHORITY"]
            elif model: classification, reasons = "MODEL_BEARING", ["MODEL_BEARING"]
            elif architecture: classification, reasons = "ARCHITECTURE_BEARING", ["ARCHITECTURE"]
            elif dependency: classification, reasons = "DEPENDENCY_EXPANDED", ["DEPENDENCY_CLOSURE"]
            elif paths: classification, reasons = "LOCAL", ["DIRECT_SURFACE_MATCH"]
            else: classification, reasons = "UNKNOWN", ["NO_CHANGED_PATHS"]
            if repair_scope_classification and repair_scope_classification != classification:
                reasons.append("VERIFIER_CLASSIFICATION_CROSS_CHECKED_AGAINST_GOVERNED_EVIDENCE")
        all_affected = tuple(sorted(set(direct) | set(transitive)))
        assurance = normalize_assurance(prior_pass_receipts)
        invalidated, preserved, historical = invalidate(assurance, set(all_affected), set(paths or ()), classification)
        rerun_tests: set[str] = set()
        for item in assurance:
            if item.assurance_id in invalidated: rerun_tests.update(item.rerun_scope)
        for unit in units:
            if str(unit.get("unit_id")) in all_affected:
                rerun_tests.update(map(str, unit.get("test_contract", unit.get("tests", ()))))
        reasons.extend(str(x) for x in broader_requalification_triggers)
        authority_needed = classification == "AUTHORITY_BEARING"
        model_needed = classification == "MODEL_BEARING"
        architecture_needed = classification == "ARCHITECTURE_BEARING"
        blocked = classification == "UNKNOWN"
        full = False
        if not blocked:
            full = len(all_affected) == len({str(u.get("unit_id")) for u in units}) and bool(units)
            full = full or (architecture_needed and bool(flags.get("all_downstream", False)))
            full = full or (authority_needed and bool(flags.get("all_execution_identity", False)))
            full = full or (model_needed and bool(flags.get("all_model_dependent", False)))
            if flags.get("insufficient_dependency_evidence", False):
                full, blocked = True, True
                reasons.append("INSUFFICIENT_DEPENDENCY_EVIDENCE")
        if blocked: reasons.append(BLOCKED_FOR_SCOPE_RESOLUTION)
        current = tuple(sorted(set(preserved)))
        material = {"run_id": run, "source": source, "classification": classification, "paths": paths or (), "direct": direct, "transitive": transitive, "invalid": invalidated, "preserved": preserved, "rerun": sorted(rerun_tests), "full": full, "status": BLOCKED_FOR_SCOPE_RESOLUTION if blocked else "PLANNED"}
        plan_id = "repair-plan-" + hashlib.sha256(_canonical(material).encode()).hexdigest()[:24]
        return RepairPlan(run, source, plan_id, classification, paths or (), tuple(sorted(direct)), tuple(sorted(transitive)), tuple(sorted(preserved)), tuple(sorted(invalidated)), tuple(sorted(rerun_tests)), tuple(sorted(all_affected)), authority_needed, model_needed, architecture_needed, full, BLOCKED_FOR_SCOPE_RESOLUTION if blocked else "PLANNED", tuple(sorted(set(reasons))), tuple(sorted(set(graph.accepted_evidence))), self.clock(), tuple(sorted(set(historical))), current)


DeterministicRepairPlanner = RepairScopePlanner
