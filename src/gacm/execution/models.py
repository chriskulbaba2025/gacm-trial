"""Machine-readable contracts for the GACM execution boundary.

These objects intentionally separate executor evidence from verification
authority.  An execution receipt can never represent authoritative PASS.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Mapping


EXECUTION_STATUSES = ("COMPLETED", "FAILED", "BLOCKED", "STOPPED")
AUTHORITY_SURFACES = ("authority", "model", "architecture")


class ExecutionBlocked(RuntimeError):
    """Raised by callers that request execution without a usable package."""

    code = "BLOCKED"


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


@dataclass(frozen=True)
class WorkUnitContract:
    run_id: str
    work_unit_id: str
    task_objective: str
    expected_outcome: str
    repository_id: str
    authorized_start_sha: str
    branch: str
    worktree: str
    context_snapshot_id: str
    context_snapshot_revision: str
    selected_model: str
    qualification_identity: str
    allowed_writable_paths: tuple[str, ...]
    forbidden_paths: tuple[str, ...]
    test_contract: tuple[str, ...]
    evidence_requirements: tuple[str, ...]
    stop_conditions: tuple[str, ...]
    broader_requalification_triggers: tuple[str, ...]
    dependencies: tuple[str, ...] = ()
    authority_status: str = "VERIFIED"
    context_status: str = "VERIFIED"
    routing_decision_id: str = ""
    model_qualified: bool = True
    rollback_authority: str = ""

    def __post_init__(self) -> None:
        required = {
            "run_id": self.run_id,
            "work_unit_id": self.work_unit_id,
            "task_objective": self.task_objective,
            "expected_outcome": self.expected_outcome,
            "repository_id": self.repository_id,
            "authorized_start_sha": self.authorized_start_sha,
            "branch": self.branch,
            "worktree": self.worktree,
            "context_snapshot_id": self.context_snapshot_id,
            "context_snapshot_revision": self.context_snapshot_revision,
            "selected_model": self.selected_model,
            "qualification_identity": self.qualification_identity,
            "routing_decision_id": self.routing_decision_id,
            "rollback_authority": self.rollback_authority,
        }
        if any(not isinstance(value, str) or not value.strip() for value in required.values()):
            raise ValueError("all execution identity and authority fields are required")
        if not self.allowed_writable_paths:
            raise ValueError("at least one allowed writable path is required")
        if not self.test_contract or not self.evidence_requirements or not self.stop_conditions:
            raise ValueError("test, evidence, and STOP contracts are required")
        # These values are retained on the contract so the adapter can return a
        # deterministic BLOCKED result for an invalid request.  Construction of
        # a request is not itself authorization to execute.

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "work_unit_id": self.work_unit_id,
            "task_objective": self.task_objective,
            "expected_outcome": self.expected_outcome,
            "repository_id": self.repository_id,
            "authorized_start_sha": self.authorized_start_sha,
            "branch": self.branch,
            "worktree": self.worktree,
            "context_snapshot_id": self.context_snapshot_id,
            "context_snapshot_revision": self.context_snapshot_revision,
            "selected_model": self.selected_model,
            "qualification_identity": self.qualification_identity,
            "allowed_writable_paths": list(self.allowed_writable_paths),
            "forbidden_paths": list(self.forbidden_paths),
            "test_contract": list(self.test_contract),
            "evidence_requirements": list(self.evidence_requirements),
            "stop_conditions": list(self.stop_conditions),
            "broader_requalification_triggers": list(self.broader_requalification_triggers),
            "dependencies": list(self.dependencies),
            "authority_status": self.authority_status,
            "context_status": self.context_status,
            "routing_decision_id": self.routing_decision_id,
            "model_qualified": self.model_qualified,
            "rollback_authority": self.rollback_authority,
        }


@dataclass(frozen=True)
class ExecutionRequest:
    contract: WorkUnitContract
    authority: Mapping[str, Any]
    operational_context: Mapping[str, Any]
    routing_decision: Mapping[str, Any]
    current_state: Mapping[str, Any]
    category_patterns: Mapping[str, tuple[str, ...]] = field(default_factory=dict)

    def machine_policy(self) -> dict[str, Any]:
        return {
            "contract": self.contract.to_dict(),
            "authority": dict(self.authority),
            "operational_context": dict(self.operational_context),
            "routing_decision": dict(self.routing_decision),
            "writable_policy": {
                "allowed": list(self.contract.allowed_writable_paths),
                "forbidden": list(self.contract.forbidden_paths),
            },
            "category_patterns": {key: list(value) for key, value in sorted(self.category_patterns.items())},
        }


@dataclass(frozen=True)
class ExecutionPackage:
    status: str
    package_id: str
    machine_policy: Mapping[str, Any]
    rendered_prompt: str
    blocking_reasons: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "package_id": self.package_id,
            "machine_policy": dict(self.machine_policy),
            "rendered_prompt": self.rendered_prompt,
            "blocking_reasons": list(self.blocking_reasons),
        }


@dataclass(frozen=True)
class RunnerResult:
    ending_sha: str | None
    files_changed: tuple[str, ...] = ()
    commands_executed: tuple[str, ...] = ()
    tests_executed: tuple[str, ...] = ()
    test_outcomes: Mapping[str, str] = field(default_factory=dict)
    evidence_artifacts: tuple[Mapping[str, Any], ...] = ()
    claimed_affected_scope: tuple[str, ...] = ()
    status: str = "COMPLETED"
    stop_reason: str | None = None
    diff_summary: str = ""
    authority_surface_changed: bool = False
    model_surface_changed: bool = False
    architecture_surface_changed: bool = False
    observed_branch: str | None = None
    observed_worktree: str | None = None
    model_used: str | None = None
    starting_sha: str | None = None


@dataclass(frozen=True)
class ExecutionReceipt:
    run_id: str
    work_unit_id: str
    execution_id: str
    starting_sha: str | None
    ending_sha: str | None
    model_used: str
    qualification_identity: str
    files_changed: tuple[str, ...]
    commands_executed: tuple[str, ...]
    tests_executed: tuple[str, ...]
    test_outcomes: Mapping[str, str]
    evidence_artifacts: tuple[Mapping[str, Any], ...]
    stop_reason: str | None
    execution_status: str
    started_at: str
    completed_at: str
    claimed_affected_scope: tuple[str, ...]
    changed_surface_flags: Mapping[str, bool]
    diff_summary: str = ""

    def __post_init__(self) -> None:
        if self.execution_status not in EXECUTION_STATUSES:
            raise ValueError(f"unsupported execution status: {self.execution_status}")
        if self.execution_status == "COMPLETED" and self.ending_sha is None:
            raise ValueError("completed execution requires an ending SHA")

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "work_unit_id": self.work_unit_id,
            "execution_id": self.execution_id,
            "starting_sha": self.starting_sha,
            "ending_sha": self.ending_sha,
            "model_used": self.model_used,
            "qualification_identity": self.qualification_identity,
            "files_changed": list(self.files_changed),
            "commands_executed": list(self.commands_executed),
            "tests_executed": list(self.tests_executed),
            "test_outcomes": dict(self.test_outcomes),
            "evidence_artifacts": [dict(item) for item in self.evidence_artifacts],
            "stop_reason": self.stop_reason,
            "execution_status": self.execution_status,
            "timestamps": {"started_at": self.started_at, "completed_at": self.completed_at},
            "claimed_affected_scope": list(self.claimed_affected_scope),
            "changed_surface_flags": dict(self.changed_surface_flags),
            "diff_summary": self.diff_summary,
            "authoritative_pass": False,
        }

    def content_sha(self) -> str:
        # Phase 2 evidence content_sha is a 40-hex Git-compatible identity.
        return hashlib.sha256(_canonical(self.to_dict()).encode("utf-8")).hexdigest()[:40]

    def to_run_state_projection(self) -> dict[str, Any]:
        """Project executor evidence without writing authoritative PASS."""

        evidence_id = "exec-" + self.execution_id
        return {
            "evidence": {
                "evidence_id": evidence_id,
                "kind": "EXECUTION_RECEIPT",
                "content_sha": self.content_sha(),
                "produced_by": "EXECUTOR",
                "recorded_at": self.completed_at,
            },
            "work_unit": {
                "unit_id": self.work_unit_id,
                "status": "VERIFYING" if self.execution_status == "COMPLETED" else "FAILED",
                "verification": {
                    "status": "NOT_RUN",
                    "authoritative": False,
                    "issuer_role": "EXECUTOR",
                },
                "output_evidence": [evidence_id],
                "affected_scope": list(self.claimed_affected_scope),
            },
        }
