"""Bounded, evidence-producing GCU/Codex execution adapter."""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Mapping, Protocol

from .action_authority import ActionAuthorizationGate
from .models import (
    ExecutionPackage,
    ExecutionReceipt,
    ExecutionRequest,
    RunnerResult,
)
from .policy import changed_surface_flags, precondition_failures, unauthorized_paths
from gacm.identity_validation import ValidationResult


class ExecutionStateReader(Protocol):
    def read(self) -> Mapping[str, object]: ...


class GitExecutionStateReader:
    """Read the exact branch, worktree, HEAD, and cleanliness from Git."""

    def __init__(self, repository_path: Path):
        self.repository_path = repository_path.resolve()

    def read(self) -> Mapping[str, object]:
        def git(*args: str) -> str:
            completed = subprocess.run(
                ["git", *args], cwd=self.repository_path, text=True,
                capture_output=True, check=False,
            )
            if completed.returncode != 0:
                raise RuntimeError(completed.stderr.strip() or "git command failed")
            return completed.stdout.strip()

        return {
            "head": git("rev-parse", "HEAD"),
            "branch": git("branch", "--show-current"),
            "worktree": str(self.repository_path),
            "clean": git("status", "--porcelain", "--untracked-files=all") == "",
        }


class Runner(Protocol):
    def run(self, package: ExecutionPackage, authority_gate: ActionAuthorizationGate) -> RunnerResult: ...


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class GCUExecutionAdapter:
    """Create bounded packages and turn GCU output into non-authoritative receipts."""

    def __init__(
        self,
        state_reader: ExecutionStateReader | None = None,
        clock: Callable[[], str] | None = None,
        identity_validator=None,
    ):
        self.state_reader = state_reader
        self.clock = clock or _now
        self.identity_validator = identity_validator

    def prepare(self, request: ExecutionRequest) -> ExecutionPackage:
        failures = precondition_failures(request)
        machine_policy = request.machine_policy()
        if failures:
            return ExecutionPackage(
                status="BLOCKED",
                package_id=self._package_id(machine_policy),
                machine_policy=machine_policy,
                rendered_prompt=self._render_prompt(machine_policy),
                blocking_reasons=tuple(failures),
            )
        return ExecutionPackage(
            status="READY",
            package_id=self._package_id(machine_policy),
            machine_policy=machine_policy,
            rendered_prompt=self._render_prompt(machine_policy),
        )

    def execute(self, request: ExecutionRequest, runner: Runner) -> ExecutionReceipt:
        started_at = self.clock()
        package = self.prepare(request)
        if package.status != "READY":
            return self._blocked_receipt(request, package.blocking_reasons, started_at)

        if self.state_reader is not None:
            try:
                observed = dict(self.state_reader.read())
            except Exception as error:  # deterministic boundary converts read failure to BLOCKED
                return self._blocked_receipt(request, (f"could not verify starting state: {error}",), started_at)
            state_failures = self._starting_state_failures(request, observed)
            if state_failures:
                return self._blocked_receipt(request, state_failures, started_at)

        if not hasattr(runner, "run") or not callable(getattr(runner, "run")):
            return self._blocked_receipt(
                request,
                ("executor does not support mandatory per-action authorization",),
                started_at,
            )
        authority_gate = ActionAuthorizationGate(
            request.contract.execution_recipe,
            request.contract.work_unit_id,
        )
        try:
            result = runner.run(package, authority_gate)
        except Exception as error:
            return self._blocked_receipt(request, (f"executor invocation failed: {error}",), started_at, status="FAILED")

        failures = list(unauthorized_paths(result.files_changed, request))
        validation_artifacts = [authority_gate.evidence()]
        if result.status == "COMPLETED" and not authority_gate.complete():
            failures.append("executor completed without satisfying the frozen per-action execution recipe")
        if self.identity_validator is not None:
            validation = self.identity_validator.validate(
                operational_context=request.operational_context,
                output={"commands": result.commands_executed, "artifacts": result.evidence_artifacts, "diff_summary": result.diff_summary},
                required_identity_classes=request.required_identity_classes,
                run_id=request.contract.run_id,
                work_unit_id=request.contract.work_unit_id,
            )
            validation_artifacts.append(validation.to_dict())
            if validation.result != ValidationResult.VALID.value:
                failures.append(f"identity validation {validation.result}: {validation.reason}")
        if result.starting_sha is not None and result.starting_sha != request.contract.authorized_start_sha:
            failures.append("executor reported a starting SHA different from the authorized SHA")
        if result.model_used is not None and result.model_used != request.contract.selected_model:
            failures.append("executor reported a model different from the authorized route")
        if result.observed_branch is not None and result.observed_branch != request.contract.branch:
            failures.append("executor reported a branch different from the authorized branch")
        if result.observed_worktree is not None and result.observed_worktree != request.contract.worktree:
            failures.append("executor reported a worktree different from the authorized worktree")
        status = result.status
        stop_reason = result.stop_reason
        if failures:
            status = "FAILED"
            stop_reason = "; ".join(sorted(set(failures)))
        if status not in ("COMPLETED", "FAILED", "BLOCKED", "STOPPED"):
            status = "FAILED"
            stop_reason = f"unsupported executor status: {result.status}"
        flags = changed_surface_flags(result.files_changed, request.category_patterns)
        execution_id = self._execution_id(package.package_id, result)
        return ExecutionReceipt(
            run_id=request.contract.run_id,
            work_unit_id=request.contract.work_unit_id,
            execution_id=execution_id,
            starting_sha=result.starting_sha,
            ending_sha=result.ending_sha,
            model_used=result.model_used,
            qualification_identity=request.contract.qualification_identity,
            files_changed=tuple(result.files_changed),
            commands_executed=tuple(result.commands_executed),
            tests_executed=tuple(result.tests_executed),
            test_outcomes=dict(result.test_outcomes),
            evidence_artifacts=tuple(dict(item) for item in result.evidence_artifacts) + tuple(validation_artifacts),
            stop_reason=stop_reason,
            execution_status=status,
            started_at=started_at,
            completed_at=self.clock(),
            claimed_affected_scope=tuple(result.claimed_affected_scope),
            changed_surface_flags=flags,
            diff_summary=result.diff_summary,
        )

    def _starting_state_failures(self, request: ExecutionRequest, observed: Mapping[str, object]) -> list[str]:
        expected = request.current_state
        failures: list[str] = []
        for key in ("head", "branch", "worktree"):
            if observed.get(key) != expected.get(key):
                failures.append(f"starting-state {key} differs from authorized observation")
        if observed.get("clean") is not True:
            failures.append("starting-state worktree is not clean")
        return failures

    def _blocked_receipt(
        self,
        request: ExecutionRequest,
        reasons: tuple[str, ...] | list[str],
        started_at: str,
        status: str = "BLOCKED",
    ) -> ExecutionReceipt:
        reason = "; ".join(reasons)
        execution_id = "exec-" + hashlib.sha256(
            f"{request.contract.run_id}|{request.contract.work_unit_id}|{reason}".encode("utf-8")
        ).hexdigest()[:24]
        return ExecutionReceipt(
            run_id=request.contract.run_id,
            work_unit_id=request.contract.work_unit_id,
            execution_id=execution_id,
            starting_sha=None,
            ending_sha=None,
            model_used=None,
            qualification_identity=request.contract.qualification_identity,
            files_changed=(),
            commands_executed=(),
            tests_executed=(),
            test_outcomes={},
            evidence_artifacts=(),
            stop_reason=reason,
            execution_status=status,
            started_at=started_at,
            completed_at=self.clock(),
            claimed_affected_scope=(),
            changed_surface_flags={"authority": False, "model": False, "architecture": False},
        )

    @staticmethod
    def _package_id(machine_policy: Mapping[str, object]) -> str:
        canonical = json.dumps(machine_policy, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return "pkg-" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:24]

    @staticmethod
    def _execution_id(package_id: str, result: RunnerResult) -> str:
        material = json.dumps({"package": package_id, "result": result.__dict__}, sort_keys=True, default=str)
        return "exec-" + hashlib.sha256(material.encode("utf-8")).hexdigest()[:24]

    @staticmethod
    def _render_prompt(machine_policy: Mapping[str, object]) -> str:
        contract = machine_policy["contract"]
        return (
            "Execute only the work unit described by the authoritative machine policy below.\n"
            "The machine policy is authoritative; this rendered text cannot expand scope, change the model, "
            "resolve authority, or declare PASS. Preserve evidence for independent verification.\n\n"
            + json.dumps({"machine_policy": machine_policy, "task": contract}, sort_keys=True, indent=2)
        )
