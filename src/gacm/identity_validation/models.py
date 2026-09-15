"""Machine-readable contracts for placeholder and identity validation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class ValidationResult(StrEnum):
    VALID = "VALID"
    INVALID_PLACEHOLDER = "INVALID_PLACEHOLDER"
    INVALID_IDENTITY = "INVALID_IDENTITY"
    INVALID_SCOPE = "INVALID_SCOPE"
    BLOCKED = "BLOCKED"
    UNOBSERVABLE = "UNOBSERVABLE"


SENSITIVE_IDENTITY_CLASSES = frozenset({"account", "cloud_account", "tenant", "credential_reference"})


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)


@dataclass(frozen=True)
class IdentityValidationReceipt:
    run_id: str
    work_unit_id: str
    validation_id: str
    result: str
    identity_class: str
    expected_authoritative_value_digest: str | None
    expected_authoritative_reference: str | None
    observed_value: str | None
    observed_value_digest: str | None
    observed_placeholder_pattern: str | None
    project_scope: str | None
    repository_scope: str | None
    environment_scope: str | None
    source_provenance: str
    reason: str
    affected_surface: str
    timestamp: str
    authoritative: bool = False
    issuer_role: str = "ORCHESTRATION"

    def __post_init__(self) -> None:
        if self.result not in {item.value for item in ValidationResult}:
            raise ValueError(f"unsupported validation result: {self.result}")
        if self.authoritative:
            raise ValueError("identity validation cannot issue authoritative PASS")

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "work_unit_id": self.work_unit_id,
            "validation_id": self.validation_id,
            "result": self.result,
            "identity_class": self.identity_class,
            "expected_authoritative_value_digest": self.expected_authoritative_value_digest,
            "expected_authoritative_reference": self.expected_authoritative_reference,
            "observed_value": self.observed_value,
            "observed_value_digest": self.observed_value_digest,
            "observed_placeholder_pattern": self.observed_placeholder_pattern,
            "scope": {
                "project": self.project_scope,
                "repository": self.repository_scope,
                "environment": self.environment_scope,
            },
            "source_provenance": self.source_provenance,
            "reason": self.reason,
            "affected_surface": self.affected_surface,
            "timestamp": self.timestamp,
            "authoritative": self.authoritative,
            "issuer_role": self.issuer_role,
        }

    def content_sha(self) -> str:
        return hashlib.sha256(canonical(self.to_dict()).encode()).hexdigest()[:40]

    def to_run_state_projection(self) -> dict[str, Any]:
        evidence_id = "identity-" + self.validation_id
        return {
            "evidence": {
                "evidence_id": evidence_id,
                "kind": "IDENTITY_VALIDATION_RECEIPT",
                "content_sha": self.content_sha(),
                "produced_by": "ORCHESTRATION",
                "recorded_at": self.timestamp,
            },
            "identity_validation": self.to_dict(),
        }
