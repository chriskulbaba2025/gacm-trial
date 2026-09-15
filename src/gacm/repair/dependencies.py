"""Deterministic dependency graph and changed-surface calculations."""

from __future__ import annotations

from collections import defaultdict, deque
from fnmatch import fnmatchcase
from pathlib import PurePosixPath
from typing import Any, Iterable, Mapping


def _match(path: str, pattern: str) -> bool:
    path = str(PurePosixPath(str(path).replace("\\", "/")))
    return path == str(pattern).replace("\\", "/") or fnmatchcase(path, str(pattern).replace("\\", "/"))


class WorkUnitDependencyGraph:
    """A graph whose edges come from work-unit contracts and proven evidence."""

    def __init__(self, work_units: Iterable[Mapping[str, Any]] = (), evidence: Iterable[Any] = ()):
        self.units = {str(u["unit_id"]): u for u in work_units if u.get("unit_id")}
        self._parents: dict[str, set[str]] = defaultdict(set)
        for child, unit in self.units.items():
            for parent in unit.get("dependencies", ()):
                if str(parent) in self.units:
                    self._parents[str(parent)].add(child)
        self.accepted_evidence: list[str] = []
        for item in evidence:
            e = item if isinstance(item, Mapping) else vars(item)
            source = str(e.get("source_kind", e.get("source", ""))).upper()
            corroborating = e.get("corroborating_evidence", e.get("corroborated_by"))
            corroborated = bool(e.get("corroborated", e.get("git_corroborated", False))) or bool(corroborating)
            if source == "GRAPHIFY" and not (corroborated and corroborating):
                continue
            if source not in {"GIT", "GITHUB", "RUN_STATE", "APPROVED_DURABLE_STATE", "GRAPHIFY"} or not corroborated:
                continue
            parent, child = str(e.get("from_unit", e.get("parent", ""))), str(e.get("to_unit", e.get("child", "")))
            if parent in self.units and child in self.units and parent != child:
                self._parents[parent].add(child)
                self.accepted_evidence.append(str(e.get("evidence_id", e.get("source_ref", source))))
        self.accepted_evidence = sorted(set(self.accepted_evidence))

    def direct_dependents(self, unit_ids: Iterable[str]) -> tuple[str, ...]:
        return tuple(sorted({child for parent in unit_ids for child in self._parents.get(str(parent), ())}))

    def transitive_dependents(self, unit_ids: Iterable[str]) -> tuple[str, ...]:
        seen: set[str] = set()
        queue = deque(sorted(str(x) for x in unit_ids))
        while queue:
            parent = queue.popleft()
            for child in sorted(self._parents.get(parent, ())):
                if child not in seen:
                    seen.add(child)
                    queue.append(child)
        return tuple(sorted(seen))

    def units_for_paths(self, paths: Iterable[str]) -> tuple[str, ...]:
        found = []
        for unit_id, unit in self.units.items():
            surfaces = unit.get("allowed_surfaces", ())
            if any(_match(path, surface) for path in paths for surface in surfaces):
                found.append(unit_id)
        return tuple(sorted(found))


def surface_flag(paths: Iterable[str], patterns: Iterable[str], explicit: bool = False) -> bool:
    return explicit or any(_match(path, pattern) for path in paths for pattern in patterns)
