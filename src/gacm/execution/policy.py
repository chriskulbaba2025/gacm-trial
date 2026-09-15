"""Deterministic policy checks owned by the GACM orchestration boundary."""

from __future__ import annotations

from fnmatch import fnmatchcase
from pathlib import PurePosixPath
from typing import Any, Iterable, Mapping

from .models import ExecutionRequest


def _path_matches(path: str, pattern: str) -> bool:
    normalized = str(PurePosixPath(path.replace("\\", "/")))
    candidate = pattern.replace("\\", "/")
    return normalized == candidate or fnmatchcase(normalized, candidate)


def path_in_surface(path: str, patterns: Iterable[str]) -> bool:
    return any(_path_matches(path, pattern) for pattern in patterns)


def precondition_failures(request: ExecutionRequest) -> list[str]:
    """Return all deterministic reasons a unit cannot be handed to GCU."""

    contract = request.contract
    authority = request.authority
    context = request.operational_context
    route = request.routing_decision
    state = request.current_state
    failures: list[str] = []

    if authority.get("status") != "VERIFIED":
        failures.append("GitHub authority resolver status is not VERIFIED")
    if context.get("status") != "VERIFIED":
        failures.append("operational context resolver status is not VERIFIED")
    if state.get("work_unit_status") != "READY":
        failures.append("work unit is not READY")
    if not route or not route.get("decision_id"):
        failures.append("routing decision is missing")
    if route.get("selected_model") != contract.selected_model:
        failures.append("selected model does not match routing decision")
    if route.get("qualification_identity") != contract.qualification_identity:
        failures.append("qualification identity does not match routing decision")
    if not contract.model_qualified:
        failures.append("selected model is not qualified")
    if not contract.rollback_authority:
        failures.append("rollback authority is missing")
    if authority.get("repository_id") != contract.repository_id:
        failures.append("repository identity does not match authorized work unit")
    if authority.get("branch") != contract.branch:
        failures.append("branch identity does not match authorized work unit")
    if authority.get("worktree") != contract.worktree:
        failures.append("worktree identity does not match authorized work unit")
    if context.get("context_id") != contract.context_snapshot_id:
        failures.append("operational-context snapshot identity does not match work unit")
    if context.get("context_revision") != contract.context_snapshot_revision:
        failures.append("operational-context snapshot revision does not match work unit")
    if state.get("head") != contract.authorized_start_sha:
        failures.append("repository HEAD does not equal authorized starting SHA")
    if state.get("branch") != contract.branch:
        failures.append("current branch does not equal authorized branch")
    if state.get("worktree") != contract.worktree:
        failures.append("current worktree does not equal authorized worktree")
    if state.get("clean") is not True:
        failures.append("worktree is not clean immediately before execution")
    if authority.get("head") != contract.authorized_start_sha:
        failures.append("authority HEAD does not equal authorized starting SHA")
    if contract.forbidden_paths is None:
        failures.append("forbidden surfaces are not explicit")
    return failures


def unauthorized_paths(changed_paths: Iterable[str], request: ExecutionRequest) -> list[str]:
    contract = request.contract
    unauthorized: list[str] = []
    for path in changed_paths:
        if path_in_surface(path, contract.forbidden_paths) or not path_in_surface(path, contract.allowed_writable_paths):
            unauthorized.append(path)
    return sorted(set(unauthorized))


def changed_surface_flags(changed_paths: Iterable[str], patterns: Mapping[str, Iterable[str]]) -> dict[str, bool]:
    paths = tuple(changed_paths)
    return {
        category: any(path_in_surface(path, category_patterns) for path in paths)
        for category, category_patterns in patterns.items()
        if category in ("authority", "model", "architecture")
    } | {category: False for category in ("authority", "model", "architecture") if category not in patterns}
