"""Independent deterministic checks used by the verification engine."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Any, Iterable, Mapping

from .scope import matches_any


class GitDiffEvidenceReader:
    """Read changed paths and a compact diff identity directly from Git."""

    def __init__(self, repository_path: Path):
        self.repository_path = repository_path.resolve()

    def read(self, starting_sha: str, ending_sha: str) -> tuple[tuple[str, ...], dict[str, Any]]:
        completed = subprocess.run(
            ["git", "diff", "--no-ext-diff", "--name-only", starting_sha, ending_sha, "--"],
            cwd=self.repository_path,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or "could not calculate Git diff")
        paths = tuple(sorted(path for path in completed.stdout.splitlines() if path))
        material = f"{starting_sha}\n{ending_sha}\n" + "\n".join(paths)
        return paths, {
            "source": "git",
            "repository": str(self.repository_path),
            "base": starting_sha,
            "head": ending_sha,
            "changed_paths": list(paths),
            "diff_identity": hashlib.sha256(material.encode("utf-8")).hexdigest()[:40],
        }


def check_paths(actual: Iterable[str] | None, allowed: Iterable[str], forbidden: Iterable[str]) -> tuple[str, list[str]]:
    if actual is None:
        return "UNOBSERVABLE", ["independent changed-path evidence is unavailable"]
    actual_paths = tuple(actual)
    unauthorized = [path for path in actual_paths if not matches_any(path, allowed)]
    forbidden_paths = [path for path in actual_paths if matches_any(path, forbidden)]
    if unauthorized:
        return "FAIL", [f"unauthorized changed path: {path}" for path in sorted(set(unauthorized))]
    if forbidden_paths:
        return "FAIL", [f"forbidden changed path: {path}" for path in sorted(set(forbidden_paths))]
    return "PASS", []


def check_repository_identity(
    contract: Mapping[str, Any],
    receipt: Mapping[str, Any],
    starting: Mapping[str, Any],
    ending: Mapping[str, Any],
) -> tuple[str, list[str]]:
    reasons: list[str] = []
    expected_sha = contract.get("authorized_start_sha")
    if starting.get("sha") != expected_sha:
        reasons.append("starting repository SHA does not match authorized starting SHA")
    if starting.get("repository_id") != contract.get("repository_id"):
        reasons.append("starting repository identity mismatch")
    if starting.get("branch") != contract.get("branch") or starting.get("worktree") != contract.get("worktree"):
        reasons.append("starting branch or worktree identity mismatch")
    if ending.get("repository_id") != contract.get("repository_id"):
        reasons.append("ending repository identity mismatch")
    if ending.get("branch") != contract.get("branch") or ending.get("worktree") != contract.get("worktree"):
        reasons.append("ending branch or worktree identity mismatch")
    if receipt.get("starting_sha") != expected_sha:
        reasons.append("executor receipt starting SHA mismatch")
    ending_sha = ending.get("sha")
    if not ending_sha or receipt.get("ending_sha") != ending_sha:
        reasons.append("executor receipt ending SHA does not match independently observed ending SHA")
    return ("FAIL", reasons) if reasons else ("PASS", [])


def check_context(contract: Mapping[str, Any], context: Mapping[str, Any]) -> tuple[str, list[str]]:
    reasons = []
    if context.get("status") != "VERIFIED":
        reasons.append("operational context is not VERIFIED")
    if context.get("context_id") != contract.get("context_snapshot_id"):
        reasons.append("operational-context snapshot identity mismatch")
    if context.get("context_revision") != contract.get("context_snapshot_revision"):
        reasons.append("operational-context snapshot revision mismatch")
    return ("FAIL", reasons) if reasons else ("PASS", [])


def check_routing(contract: Mapping[str, Any], route: Mapping[str, Any], receipt: Mapping[str, Any]) -> tuple[str, list[str]]:
    reasons = []
    if route.get("decision_id") != contract.get("routing_decision_id"):
        reasons.append("routing decision identity mismatch")
    if route.get("selected_model") != contract.get("selected_model"):
        reasons.append("routing selected model mismatch")
    if route.get("qualification_identity") != contract.get("qualification_identity"):
        reasons.append("routing qualification identity mismatch")
    if receipt.get("model_used") != contract.get("selected_model"):
        reasons.append("executor model differs from authorized model")
    if receipt.get("qualification_identity") != contract.get("qualification_identity"):
        reasons.append("executor qualification differs from authorized qualification")
    return ("FAIL", reasons) if reasons else ("PASS", [])


def check_tests(contract: Mapping[str, Any], test_contract: Iterable[str], outcomes: Mapping[str, str] | None) -> tuple[str, list[str]]:
    required = tuple(test_contract)
    if outcomes is None:
        return "UNOBSERVABLE", ["independent test outcomes are unavailable"]
    missing = [name for name in required if name not in outcomes]
    failed = [name for name in required if outcomes.get(name) != "PASS"]
    if missing:
        return "UNOBSERVABLE", [f"required test outcome unavailable: {name}" for name in missing]
    if failed:
        return "FAIL", [f"required test did not PASS: {name}" for name in failed]
    return "PASS", []


def check_executor_claim(receipt: Mapping[str, Any]) -> tuple[str, list[str]]:
    if receipt.get("authoritative_pass") is True:
        return "FAIL", ["executor receipt claims authoritative PASS"]
    verification = receipt.get("verification")
    if isinstance(verification, Mapping) and (verification.get("status") == "PASS" or verification.get("authoritative") is True):
        return "FAIL", ["executor-issued verification PASS is not accepted"]
    return "PASS", []
