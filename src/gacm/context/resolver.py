"""Deterministic authoritative operational-context resolution."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from gacm.authority.resolver import ResolutionResult

from .models import ContextCandidate, ContextSnapshot, SourceProvenance
from .requirements import OperationRequirements


SHA_RE = re.compile(r"^[0-9a-f]{40}$")
PLACEHOLDER_RE = re.compile(
    r"^(?:<[^>]+>|your(?:[_-].*)?|replace(?:[_-].*)?|insert(?:[_-].*)?|example(?:[_-].*)?|default(?:[_-].*)?)$",
    re.IGNORECASE,
)


class ContextResolver:
    """Resolve exactly one GitHub-backed candidate for each required field."""

    def __init__(
        self,
        requirements: OperationRequirements,
        authority: ResolutionResult,
        repository_path: Path,
    ):
        self.requirements = requirements
        self.authority = authority
        self.repository_path = repository_path.resolve()

    def resolve(self, candidates: Iterable[ContextCandidate]) -> ContextSnapshot:
        candidate_list = list(candidates)
        if self.authority.status != "VERIFIED":
            return self._blocked("GitHub authority must be VERIFIED before context resolution")
        if not self.authority.local_head or not self.authority.remote_url:
            return self._blocked("verified GitHub authority lacks repository identity")
        if not candidate_list:
            return self._blocked("required authoritative operational data is missing")

        invalid: list[str] = []
        by_field: dict[str, list[ContextCandidate]] = {}
        for candidate in candidate_list:
            reason = self._validate_candidate(candidate)
            if reason:
                invalid.append(reason)
            elif candidate.field in self.requirements.required_fields:
                by_field.setdefault(candidate.field, []).append(candidate)

        if invalid:
            return self._blocked(*invalid)

        missing = [field for field in self.requirements.required_fields if field not in by_field]
        if missing:
            return self._blocked("required authoritative fields are missing: " + ", ".join(missing))
        ambiguous = [field for field in self.requirements.required_fields if len(by_field[field]) != 1]
        if ambiguous:
            return self._ambiguous("multiple authoritative candidates remain: " + ", ".join(ambiguous))

        selected = {field: by_field[field][0] for field in self.requirements.required_fields}
        values = {field: selected[field].value for field in self.requirements.required_fields}
        sources = tuple(
            {"field": field, **selected[field].provenance.to_dict()}
            for field in self.requirements.required_fields
        )
        canonical = json.dumps(
            {"operation": self.requirements.operation, "values": values, "sources": list(sources)},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        context_id = "ctx-" + hashlib.sha256(canonical).hexdigest()[:32]
        revision = hashlib.sha256((self.authority.local_head + canonical.decode("utf-8")).encode("utf-8")).hexdigest()
        return ContextSnapshot(
            status="VERIFIED",
            operation=self.requirements.operation,
            context_id=context_id,
            context_revision=revision,
            values=values,
            sources=sources,
            authority_head=self.authority.local_head,
            repository_remote=self.authority.remote_url,
        )

    def _validate_candidate(self, candidate: ContextCandidate) -> str | None:
        provenance = candidate.provenance
        if candidate.field not in self.requirements.required_fields:
            return None
        if provenance.source_kind != "GITHUB" or not provenance.github_proof:
            return f"field {candidate.field} is not backed by verified GitHub proof"
        if not SHA_RE.fullmatch(provenance.source_git_head) or not SHA_RE.fullmatch(provenance.source_blob_sha):
            return f"field {candidate.field} has invalid Git provenance identity"
        if provenance.source_git_head != self.authority.local_head:
            return f"field {candidate.field} comes from a different Git HEAD"
        if provenance.repository_id != self.authority.repository:
            return f"field {candidate.field} has wrong repository provenance"
        if self.requirements.expected_repository and provenance.repository_id != self.requirements.expected_repository:
            return f"field {candidate.field} has wrong configured repository provenance"
        if self.requirements.expected_project and provenance.project_id != self.requirements.expected_project:
            return f"field {candidate.field} has wrong project provenance"
        if self.requirements.expected_environment and provenance.environment != self.requirements.expected_environment:
            return f"field {candidate.field} has wrong environment provenance"
        if candidate.field == "project" and candidate.value != provenance.project_id:
            return "project value does not match its source project provenance"
        if candidate.field == "repository" and candidate.value != provenance.repository_id:
            return "repository value does not match its source repository provenance"
        if candidate.field == "environment" and provenance.environment and candidate.value != provenance.environment:
            return "environment value does not match its source environment provenance"
        if _contains_placeholder(candidate.value):
            return f"field {candidate.field} contains a placeholder or example value"
        source_path = provenance.source_path.replace("\\", "/")
        if not _safe_relative_source(source_path):
            return f"field {candidate.field} has unsafe source path"
        if not self._source_matches_git_head(source_path, provenance.source_blob_sha):
            return f"field {candidate.field} source is not present in the verified Git HEAD"
        return None

    def _source_matches_git_head(self, source_path: str, blob_sha: str) -> bool:
        assert self.authority.local_head
        object_name = f"{self.authority.local_head}:{source_path}"
        exists = subprocess.run(
            ["git", "cat-file", "-e", object_name],
            cwd=self.repository_path,
            text=True,
            capture_output=True,
            check=False,
        )
        if exists.returncode != 0:
            return False
        blob = subprocess.run(
            ["git", "rev-parse", object_name],
            cwd=self.repository_path,
            text=True,
            capture_output=True,
            check=False,
        )
        return blob.returncode == 0 and blob.stdout.strip() == blob_sha

    def _blocked(self, *reasons: str) -> ContextSnapshot:
        return ContextSnapshot(
            status="BLOCKED",
            operation=self.requirements.operation,
            context_id=None,
            context_revision=None,
            values={},
            sources=(),
            authority_head=self.authority.local_head,
            repository_remote=self.authority.remote_url,
            blocking_reasons=tuple(reasons),
        )

    def _ambiguous(self, *reasons: str) -> ContextSnapshot:
        return ContextSnapshot(
            status="AMBIGUOUS",
            operation=self.requirements.operation,
            context_id=None,
            context_revision=None,
            values={},
            sources=(),
            authority_head=self.authority.local_head,
            repository_remote=self.authority.remote_url,
            ambiguous_reasons=tuple(reasons),
        )


def candidate_from_handoff(
    field: str,
    value: Any,
    handoff_candidate: dict[str, Any],
    project_id: str,
    repository_id: str,
    environment: str | None = None,
) -> ContextCandidate:
    """Convert Phase 4 source-presence proof into a context candidate."""

    required = ("source_path", "source_blob_sha", "source_git_head")
    if any(not handoff_candidate.get(key) for key in required):
        raise ValueError("handoff candidate lacks GitHub source proof")
    return ContextCandidate(
        field=field,
        value=value,
        provenance=SourceProvenance(
            source_kind="GITHUB",
            source_path=handoff_candidate["source_path"],
            source_blob_sha=handoff_candidate["source_blob_sha"],
            source_git_head=handoff_candidate["source_git_head"],
            repository_id=repository_id,
            project_id=project_id,
            environment=environment,
            query=handoff_candidate.get("query"),
            github_proof=True,
        ),
    )


def _contains_placeholder(value: Any) -> bool:
    if isinstance(value, str):
        normalized = value.strip()
        return bool(PLACEHOLDER_RE.fullmatch(normalized)) or normalized.lower() in {
            "your_account",
            "your_region",
            "your_repo",
            "replace_this",
            "insert_your",
        }
    if isinstance(value, dict):
        return any(_contains_placeholder(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_placeholder(item) for item in value)
    return False


def _safe_relative_source(value: str) -> bool:
    if not value or value.startswith("/") or re.match(r"^[A-Za-z]:", value) or "\x00" in value:
        return False
    parts = PurePosixPath(value).parts
    return bool(parts) and ".." not in parts and not any(part == "" for part in parts)
