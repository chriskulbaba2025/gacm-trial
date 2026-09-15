"""Assurance invalidation rules; historical receipts are never rewritten."""

from __future__ import annotations

from fnmatch import fnmatchcase
from typing import Iterable

from .models import AssuranceRecord


def normalize_assurance(items: Iterable[AssuranceRecord | dict]) -> tuple[AssuranceRecord, ...]:
    result = []
    for item in items:
        if isinstance(item, AssuranceRecord):
            result.append(item)
            continue
        data = dict(item)
        result.append(AssuranceRecord(
            assurance_id=str(data.get("assurance_id", "")),
            surfaces=tuple(sorted(map(str, data.get("surfaces", ())))),
            depends_on=tuple(sorted(map(str, data.get("depends_on", ())))),
            rerun_scope=tuple(sorted(map(str, data.get("rerun_scope", ())))),
            work_unit_id=str(data["work_unit_id"]) if data.get("work_unit_id") is not None else None,
            historical_status=str(data.get("historical_status", "PASS")),
            current_reliability=str(data.get("current_reliability", "CURRENTLY_RELIABLE")),
            receipt=data.get("receipt", {}),
        ))
    return tuple(sorted(result, key=lambda x: x.assurance_id))


def invalidate(assurance: Iterable[AssuranceRecord], affected_units: set[str], changed_paths: set[str], classification: str) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    invalid, preserved, historical = [], [], []
    categories = {classification.lower().replace("_bearing", "").replace("_expanded", "")}
    for record in assurance:
        if record.historical_status == "PASS":
            historical.append(record.assurance_id)
        surface_hit = any(path == surface or fnmatchcase(path, surface) for path in changed_paths for surface in record.surfaces)
        unit_hit = record.work_unit_id in affected_units if record.work_unit_id else False
        dependency_categories = {item.lower().replace("_bearing", "").replace("_expanded", "") for item in record.depends_on}
        category_hit = bool(categories.intersection(dependency_categories))
        affected = surface_hit or unit_hit or category_hit or (classification == "UNKNOWN")
        if affected:
            invalid.append(record.assurance_id)
        else:
            preserved.append(record.assurance_id)
    return tuple(sorted(set(invalid))), tuple(sorted(set(preserved))), tuple(sorted(set(historical)))
