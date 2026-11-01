"""Deterministic repair-scope and assurance classification."""

from __future__ import annotations

from fnmatch import fnmatchcase
from pathlib import PurePosixPath
import re
from typing import Any, Iterable, Mapping

from .models import ScopeDetermination


def path_matches(path: str, pattern: str) -> bool:
    raw = path.replace("\\", "/")
    if raw.startswith("/") or re.match(r"^[A-Za-z]:/", raw) or ".." in raw.split("/"):
        return False
    normalized = str(PurePosixPath(raw))
    return normalized == pattern.replace("\\", "/") or fnmatchcase(normalized, pattern.replace("\\", "/"))


def matches_any(path: str, patterns: Iterable[str]) -> bool:
    return any(path_matches(path, pattern) for pattern in patterns)


def determine_scope(
    changed_paths: Iterable[str],
    scope_patterns: Mapping[str, Iterable[str]],
    dependency_paths: Iterable[str],
    prior_assurance: Iterable[Mapping[str, Any]],
) -> ScopeDetermination:
    changed = tuple(sorted(set(changed_paths)))
    authority = any(matches_any(path, scope_patterns.get("authority", ())) for path in changed)
    model = any(matches_any(path, scope_patterns.get("model", ())) for path in changed)
    architecture = any(matches_any(path, scope_patterns.get("architecture", ())) for path in changed)
    dependency = any(matches_any(path, dependency_paths) for path in changed)

    if authority:
        classification = "AUTHORITY_BEARING"
        reasons = ("SHARED_AUTHORITY",)
    elif model:
        classification = "MODEL_BEARING"
        reasons = ("MODEL_BEARING",)
    elif architecture:
        classification = "ARCHITECTURE_BEARING"
        reasons = ("ARCHITECTURE",)
    elif dependency:
        classification = "DEPENDENCY_EXPANDED"
        reasons = ("HIGH_BLAST_RADIUS_DEPENDENCY",)
    elif changed:
        classification = "LOCAL"
        reasons = ()
    else:
        classification = "UNKNOWN"
        reasons = ("NO_CHANGED_PATH_OBSERVATION",)

    invalidated: list[str] = []
    preserved: list[str] = []
    rerun: set[str] = set(changed)
    for assurance in prior_assurance:
        assurance_id = str(assurance.get("assurance_id", ""))
        surfaces = tuple(str(item) for item in assurance.get("surfaces", ()))
        depends = set(str(item) for item in assurance.get("depends_on", ()))
        affected = any(matches_any(path, surfaces) or path in surfaces for path in changed)
        if classification == "DEPENDENCY_EXPANDED" and (affected or "dependency" in depends):
            affected = True
        if classification == "AUTHORITY_BEARING" and (affected or "authority" in depends):
            affected = True
        if classification == "MODEL_BEARING" and (affected or "model" in depends):
            affected = True
        if classification == "ARCHITECTURE_BEARING" and (affected or "architecture" in depends):
            affected = True
        if classification == "UNKNOWN":
            affected = True
        if affected:
            invalidated.append(assurance_id)
            rerun.update(str(item) for item in assurance.get("rerun_scope", ()))
        else:
            preserved.append(assurance_id)

    broader = classification in {"DEPENDENCY_EXPANDED", "AUTHORITY_BEARING", "MODEL_BEARING", "ARCHITECTURE_BEARING", "UNKNOWN"}
    return ScopeDetermination(
        classification=classification,
        changed_paths=changed,
        affected_scope=changed,
        broader_requalification_required=broader,
        requalification_reasons=reasons,
        prior_assurance_invalidated=tuple(sorted(item for item in invalidated if item)),
        prior_assurance_preserved=tuple(sorted(item for item in preserved if item)),
        rerun_scope=tuple(sorted(rerun)),
    )
