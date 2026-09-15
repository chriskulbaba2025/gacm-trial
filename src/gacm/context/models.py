"""Immutable, provenance-bearing operational-context models."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


@dataclass(frozen=True)
class SourceProvenance:
    source_kind: str
    source_path: str
    source_blob_sha: str
    source_git_head: str
    repository_id: str
    project_id: str
    environment: str | None = None
    query: str | None = None
    github_proof: bool = False

    def to_dict(self) -> dict[str, Any]:
        result = {
            "source_kind": self.source_kind,
            "source_path": self.source_path,
            "source_blob_sha": self.source_blob_sha,
            "source_git_head": self.source_git_head,
            "repository_id": self.repository_id,
            "project_id": self.project_id,
            "github_proof": self.github_proof,
        }
        if self.environment is not None:
            result["environment"] = self.environment
        if self.query is not None:
            result["query"] = self.query
        return result


@dataclass(frozen=True)
class ContextCandidate:
    field: str
    value: Any
    provenance: SourceProvenance


@dataclass(frozen=True)
class ContextSnapshot:
    status: str
    operation: str
    context_id: str | None
    context_revision: str | None
    values: Mapping[str, Any]
    sources: tuple[Mapping[str, Any], ...]
    authority_head: str | None
    repository_remote: str | None = None
    blocking_reasons: tuple[str, ...] = ()
    ambiguous_reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "values", _freeze(dict(self.values)))
        object.__setattr__(self, "sources", tuple(_freeze(dict(source)) for source in self.sources))

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "operation": self.operation,
            "context_id": self.context_id,
            "context_revision": self.context_revision,
            "values": _thaw(self.values),
            "sources": [_thaw(source) for source in self.sources],
            "authority_head": self.authority_head,
            "blocking_reasons": list(self.blocking_reasons),
            "ambiguous_reasons": list(self.ambiguous_reasons),
        }

    def to_run_state_patch(self, protected_rollback_sha: str) -> dict[str, Any]:
        if self.status != "VERIFIED":
            raise ValueError("only VERIFIED context can populate run state")
        values = _thaw(self.values)
        required = {"project", "client", "repository", "branch", "environment", "cloud_account", "tenant", "region", "deployment_target"}
        missing = sorted(required - set(values))
        if missing:
            raise ValueError(f"verified context lacks run-state fields: {', '.join(missing)}")
        if not self.authority_head:
            raise ValueError("verified context lacks authoritative Git head")
        if not self.repository_remote:
            raise ValueError("verified context lacks authoritative repository remote")
        cloud = values["cloud_account"]
        cloud_id = cloud.get("account_id") if isinstance(cloud, dict) else cloud
        repository_id = values["repository"]
        if not re.fullmatch(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$", repository_id):
            repository_id = "repo-" + hashlib.sha256(repository_id.encode("utf-8")).hexdigest()[:32]
        patch = {
            "current_repository_sha": self.authority_head,
            "repository": {
                "repository_id": repository_id,
                "remote": self.repository_remote,
                "branch": values["branch"],
                "worktree": "<resolver-worktree>",
                "protected_rollback_sha": protected_rollback_sha,
            },
            "operational_context": {
                "resolution_status": "RESOLVED",
                "context_id": self.context_id,
                "context_revision": self.context_revision,
                "authority_source": {"kind": "GITHUB", "ref": "HEAD", "content_sha": self.authority_head},
                "account_id": cloud_id,
                "tenant_id": values["tenant"],
                "client_id": values["client"],
                "project_id": values["project"],
                "repository_id": repository_id,
                "branch": values["branch"],
                "environment": values["environment"],
                "cloud_account_id": cloud_id,
                "region": values["region"],
                "deployment_target": values["deployment_target"],
            },
        }
        if "credential_reference" in values:
            refs = values["credential_reference"]
            patch["operational_context"]["credential_references"] = refs if isinstance(refs, list) else [refs]
        return patch

    def assert_unchanged(self, authority_head: str, source_blob_shas: Mapping[str, str]) -> None:
        if self.status != "VERIFIED":
            raise ValueError("only VERIFIED context snapshots can be bound")
        if authority_head != self.authority_head:
            raise RuntimeError("operational authority changed; create a new snapshot or invalidate the unit")
        expected = {source["source_path"]: source["source_blob_sha"] for source in self.sources}
        if any(source_blob_shas.get(path) != sha for path, sha in expected.items()):
            raise RuntimeError("operational source changed; create a new snapshot or invalidate the unit")
