"""Bounded Graphify discovery adapter.

Graphify output is treated as untrusted discovery. GitHub authority proof is a
separate handoff step and never changes a discovery result into VERIFIED.
"""

from __future__ import annotations

import hashlib
import json
import ntpath
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Sequence

from gacm.authority.resolver import ResolutionResult

from .models import Candidate, DiscoveryResult, HandoffResult


CommandRunner = Callable[[Sequence[str], str, float, Path], "CommandResult"]


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str = ""


@dataclass(frozen=True)
class GraphifyConfig:
    command: tuple[str, ...]
    repository_path: Path
    query: str
    max_results: int = 20
    timeout_seconds: float = 10.0
    repository_identity: str | None = None


def default_command_runner(command: Sequence[str], payload: str, timeout: float, cwd: Path) -> CommandResult:
    try:
        completed = subprocess.run(
            list(command),
            cwd=cwd,
            input=payload,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as error:
        raise error
    return CommandResult(completed.returncode, completed.stdout, completed.stderr)


class GraphifyAdapter:
    """Execute configured Graphify and validate discovery provenance."""

    def __init__(self, config: GraphifyConfig, runner: CommandRunner | None = None):
        if not config.command:
            raise ValueError("Graphify command must not be empty")
        if config.max_results < 1:
            raise ValueError("max_results must be positive")
        if config.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.config = config
        self.runner = runner or default_command_runner

    def discover(self) -> DiscoveryResult:
        payload = json.dumps(
            {
                "query": self.config.query,
                "repository_path": str(self.config.repository_path.resolve()),
                "max_results": self.config.max_results,
            },
            sort_keys=True,
        )
        try:
            command_result = self.runner(
                self.config.command,
                payload,
                self.config.timeout_seconds,
                self.config.repository_path,
            )
        except FileNotFoundError:
            return DiscoveryResult("ERROR", self.config.query, error="Graphify command is unavailable")
        except subprocess.TimeoutExpired:
            return DiscoveryResult("ERROR", self.config.query, error="Graphify command timed out")
        except OSError as error:
            return DiscoveryResult("ERROR", self.config.query, error=f"Graphify execution failed: {error}")

        if command_result.returncode != 0:
            detail = command_result.stderr.strip() or "Graphify command returned a non-zero exit code"
            return DiscoveryResult("ERROR", self.config.query, error=detail)
        try:
            raw = json.loads(command_result.stdout)
        except json.JSONDecodeError:
            return DiscoveryResult("ERROR", self.config.query, error="Graphify output is not valid JSON")
        try:
            candidates = self._parse_candidates(raw)
        except ValueError as error:
            return DiscoveryResult("ERROR", self.config.query, error=str(error))

        if not candidates:
            return DiscoveryResult("NO_MATCH", self.config.query)
        if len(candidates) > self.config.max_results:
            return DiscoveryResult("ERROR", self.config.query, error="Graphify returned more than max_results")
        status = "DISCOVERED" if len(candidates) == 1 else "AMBIGUOUS"
        return DiscoveryResult(status, self.config.query, candidates=candidates)

    def _parse_candidates(self, raw: Any) -> list[Candidate]:
        if not isinstance(raw, dict) or not isinstance(raw.get("candidates"), list):
            raise ValueError("Graphify output must be an object with a candidates array")
        candidates: list[Candidate] = []
        for index, item in enumerate(raw["candidates"]):
            if not isinstance(item, dict):
                raise ValueError(f"candidate {index} is not an object")
            source_path = item.get("source_path")
            source_type = item.get("source_type")
            relationship = item.get("relationship")
            target = item.get("target")
            candidate_query = item.get("query")
            confidence = item.get("confidence")
            if not all(isinstance(value, str) and value.strip() for value in (source_path, source_type, relationship, target, candidate_query)):
                raise ValueError(f"candidate {index} lacks required provenance fields")
            if candidate_query != self.config.query:
                raise ValueError(f"candidate {index} query does not match requested query")
            if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= confidence <= 1:
                raise ValueError(f"candidate {index} confidence must be between 0 and 1")
            if not _safe_relative_source(source_path):
                raise ValueError(f"candidate {index} source_path is not a safe relative path")
            candidate_repository = item.get("repository")
            if candidate_repository is not None and not isinstance(candidate_repository, str):
                raise ValueError(f"candidate {index} repository identity is invalid")
            if self.config.repository_identity and candidate_repository and candidate_repository != self.config.repository_identity:
                raise ValueError(f"candidate {index} repository identity conflicts with configured repository")
            candidates.append(
                Candidate(
                    source_path=source_path,
                    source_type=source_type,
                    relationship=relationship,
                    target=target,
                    confidence=float(confidence),
                    query=candidate_query,
                    workspace=str(self.config.repository_path.resolve()),
                    repository=candidate_repository or self.config.repository_identity,
                    source_revision=item.get("source_revision"),
                )
            )
        return candidates


def handoff_candidates(
    discovery: DiscoveryResult,
    authority: ResolutionResult,
    repository_path: Path,
) -> HandoffResult:
    """Prove candidate source presence in the exact verified Git HEAD.

    The return status is deliberately not VERIFIED and contains no authority
    fields. It only says whether a candidate is ready for a later context layer
    to evaluate.
    """

    if discovery.status not in {"DISCOVERED", "AMBIGUOUS"}:
        return HandoffResult("REJECTED", rejection_reasons=["discovery result is not usable for source handoff"])
    if authority.status != "VERIFIED" or not authority.local_head:
        return HandoffResult("REJECTED", rejection_reasons=["GitHub authority result is not VERIFIED"])
    accepted: list[dict[str, Any]] = []
    rejected: list[str] = []
    for candidate in discovery.candidates:
        source = _git_source_path(candidate.source_path)
        completed = subprocess.run(
            ["git", "cat-file", "-e", f"{authority.local_head}:{source}"],
            cwd=repository_path,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            rejected.append(f"candidate source is absent from verified Git HEAD: {candidate.source_path}")
            continue
        blob = subprocess.run(
            ["git", "rev-parse", f"{authority.local_head}:{source}"],
            cwd=repository_path,
            text=True,
            capture_output=True,
            check=False,
        )
        if blob.returncode != 0:
            rejected.append(f"candidate source identity could not be resolved: {candidate.source_path}")
            continue
        accepted.append(
            {
                "source_path": candidate.source_path,
                "source_type": candidate.source_type,
                "relationship": candidate.relationship,
                "target": candidate.target,
                "query": candidate.query,
                "source_git_head": authority.local_head,
                "source_blob_sha": blob.stdout.strip(),
            }
        )
    if rejected:
        return HandoffResult("REJECTED", candidates=accepted, rejection_reasons=rejected)
    return HandoffResult("ACCEPTED_FOR_AUTHORITY_RESOLUTION", candidates=accepted)


def discovery_evidence(result: DiscoveryResult, evidence_id: str, recorded_at: str) -> dict[str, Any]:
    """Create a Phase 2 evidence record without asserting authority."""

    raw = json.dumps(result.to_dict(), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "evidence_id": evidence_id,
        "kind": "graphify-discovery",
        "content_sha": hashlib.sha1(raw).hexdigest(),
        "produced_by": "ORCHESTRATION",
        "recorded_at": recorded_at,
    }


def _safe_relative_source(value: str) -> bool:
    if value.startswith("/") or ntpath.isabs(value) or "\x00" in value:
        return False
    parts = PurePosixPath(value.replace("\\", "/")).parts
    return bool(parts) and ".." not in parts and not any(part == "" for part in parts)


def _git_source_path(value: str) -> str:
    return value.replace("\\", "/")
