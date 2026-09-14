"""Data models for provenance-bearing Graphify discovery results."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Candidate:
    source_path: str
    source_type: str
    relationship: str
    target: str
    confidence: float
    query: str
    workspace: str
    repository: str | None = None
    source_revision: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {key: value for key, value in asdict(self).items() if value is not None}


@dataclass
class DiscoveryResult:
    status: str
    query: str
    candidates: list[Candidate] = field(default_factory=list)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "status": self.status,
            "query": self.query,
            "candidates": [candidate.to_dict() for candidate in self.candidates],
        }
        if self.error is not None:
            payload["error"] = self.error
        return payload


@dataclass
class HandoffResult:
    """Result of source-presence proof, not an authority promotion."""

    status: str
    candidates: list[dict[str, Any]] = field(default_factory=list)
    rejection_reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "candidates": self.candidates,
            "rejection_reasons": self.rejection_reasons,
        }
