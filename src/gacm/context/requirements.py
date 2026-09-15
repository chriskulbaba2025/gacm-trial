"""Deterministic required-identity declarations for an operation."""

from __future__ import annotations

from dataclasses import dataclass


SUPPORTED_CONTEXT_FIELDS = (
    "project",
    "client",
    "repository",
    "branch",
    "environment",
    "cloud_account",
    "tenant",
    "region",
    "deployment_target",
    "service",
    "database",
    "credential_reference",
    "domain",
    "external_integration_identity",
)


@dataclass(frozen=True)
class OperationRequirements:
    operation: str
    required_fields: tuple[str, ...]
    expected_project: str | None = None
    expected_repository: str | None = None
    expected_environment: str | None = None

    def __post_init__(self) -> None:
        if not self.operation.strip():
            raise ValueError("operation must not be empty")
        if not self.required_fields:
            raise ValueError("at least one required context field is needed")
        unknown = sorted(set(self.required_fields) - set(SUPPORTED_CONTEXT_FIELDS))
        if unknown:
            raise ValueError(f"unsupported context fields: {', '.join(unknown)}")
        if len(set(self.required_fields)) != len(self.required_fields):
            raise ValueError("required context fields must be unique")
