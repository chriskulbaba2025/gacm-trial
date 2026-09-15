"""Deterministic validation before independent verification."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any, Callable, Iterable

from .models import IdentityValidationReceipt, SENSITIVE_IDENTITY_CLASSES, ValidationResult, canonical
from .patterns import PlaceholderPatterns


IDENTITY_ALIASES = {
    "project": "project", "client": "client", "repository": "repository", "repo": "repository",
    "branch": "branch", "environment": "environment", "cloud_account": "cloud_account",
    "account": "cloud_account", "tenant": "tenant", "region": "region", "deployment_target": "deployment_target",
    "service": "service", "database": "database", "credential_reference": "credential_reference",
    "domain": "domain", "external_integration": "external_integration",
}


class PlaceholderIdentityValidator:
    def __init__(self, patterns: PlaceholderPatterns | None = None, clock: Callable[[], str] | None = None):
        self.patterns = patterns or PlaceholderPatterns()
        self.clock = clock or (lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    def validate(self, *, operational_context: Mapping[str, Any] | Any, output: Any,
                 required_identity_classes: Iterable[str], run_id: str, work_unit_id: str,
                 project_scope: str | None = None, repository_scope: str | None = None,
                 environment_scope: str | None = None, source_provenance: Any = "EXECUTION_OUTPUT",
                 context_snapshot_id: str | None = None, context_snapshot_revision: str | None = None,
                 authority_head: str | None = None, active_project: str | None = None,
                 active_repository: str | None = None, active_environment: str | None = None) -> IdentityValidationReceipt:
        context = operational_context.to_dict() if hasattr(operational_context, "to_dict") else dict(operational_context)
        values = context.get("values") if isinstance(context.get("values"), Mapping) else context
        status = str(context.get("status", context.get("resolution_status", ""))).upper()
        if status not in {"VERIFIED", "RESOLVED"}:
            return self._receipt(run_id, work_unit_id, "", ValidationResult.BLOCKED, "context", None, None, "operational context is not verified", source_provenance, context, "context is ambiguous, missing, or unverified")
        if context_snapshot_id and context.get("context_id") != context_snapshot_id:
            return self._receipt(run_id, work_unit_id, "", ValidationResult.BLOCKED, "context", None, None, "stale operational-context snapshot identity", source_provenance, context, "context snapshot identity is stale")
        if context_snapshot_revision and context.get("context_revision") != context_snapshot_revision:
            return self._receipt(run_id, work_unit_id, "", ValidationResult.BLOCKED, "context", None, None, "stale operational-context snapshot revision", source_provenance, context, "context snapshot revision is stale")
        if authority_head and context.get("authority_head") and context.get("authority_head") != authority_head:
            return self._receipt(run_id, work_unit_id, "", ValidationResult.BLOCKED, "context", None, None, "operational context authority head is stale", source_provenance, context, "context authority head changed")
        if active_project and values.get("project") != active_project or active_repository and values.get("repository") != active_repository or active_environment and values.get("environment") != active_environment:
            return self._receipt(run_id, work_unit_id, "", ValidationResult.INVALID_SCOPE, "context", None, None, "context does not match active project, repository, or environment scope", source_provenance, context, "active execution scope mismatch")
        provenance = self._provenance(context, source_provenance)
        if provenance.upper() in {"CHAT", "MODEL", "MEMORY", "CHAT_MEMORY"}:
            return self._receipt(run_id, work_unit_id, "", ValidationResult.INVALID_IDENTITY, "context", None, None, "identity is sourced only from chat or model memory", provenance, context, "untrusted identity provenance")
        raw = self._text(output)
        if raw is None:
            return self._receipt(run_id, work_unit_id, "", ValidationResult.UNOBSERVABLE, "output", None, None, "output cannot be parsed as text or structured data", provenance, context, "unparsable output")
        found = self.patterns.find(raw)
        required = tuple(dict.fromkeys(IDENTITY_ALIASES.get(str(item).lower(), str(item).lower()) for item in required_identity_classes))
        if not required:
            required = tuple(k for k in IDENTITY_ALIASES.values() if k in values)
        for identity_class in required:
            expected = self._value(values, identity_class)
            if expected is None or expected == "":
                return self._receipt(run_id, work_unit_id, "", ValidationResult.BLOCKED, identity_class, None, None, "required authoritative identity is unavailable", provenance, context, "authoritative value is unresolved")
            expected = str(expected)
            relevant = [match for match in found if self._match_class(match.text, identity_class)]
            if relevant:
                match = relevant[0]
                return self._receipt(run_id, work_unit_id, raw, ValidationResult.INVALID_PLACEHOLDER, identity_class, expected, match.text, "placeholder or user re-prompt detected where authoritative identity exists", provenance, context, "placeholder pattern: " + match.text)
            candidates = self._candidates(raw, identity_class)
            if candidates and expected not in candidates:
                observed = candidates[0]
                if self._scope_mismatch(identity_class, observed, values, project_scope or active_project or str(values.get("project", "")), repository_scope or active_repository or str(values.get("repository", "")), environment_scope or active_environment or str(values.get("environment", ""))):
                    result, reason = ValidationResult.INVALID_SCOPE, "observed identity belongs to another project, repository, or environment scope"
                else:
                    result, reason = ValidationResult.INVALID_IDENTITY, "observed identity differs from authoritative context"
                return self._receipt(run_id, work_unit_id, raw, result, identity_class, expected, observed, reason, provenance, context, reason)
            if expected not in raw:
                return self._receipt(run_id, work_unit_id, raw, ValidationResult.UNOBSERVABLE, identity_class, expected, None, "required identity was not observable in output", provenance, context, "required authoritative identity missing from output")
        return self._receipt(run_id, work_unit_id, raw, ValidationResult.VALID, required[0] if required else "", None, None, "all required identities match verified context", provenance, context, "validated")

    @staticmethod
    def _text(output: Any) -> str | None:
        if isinstance(output, str): return output
        if isinstance(output, Mapping) or isinstance(output, (list, tuple)):
            try: return json.dumps(output, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
            except (TypeError, ValueError): return None
        return None

    @staticmethod
    def _provenance(context: Mapping[str, Any], supplied: Any) -> str:
        if isinstance(supplied, Mapping):
            return str(supplied.get("source_kind", supplied.get("kind", "UNKNOWN")))
        sources = context.get("sources", ())
        if sources and isinstance(sources[0], Mapping): return str(sources[0].get("source_kind", sources[0].get("kind", "UNKNOWN")))
        return str(supplied)

    @staticmethod
    def _value(values: Mapping[str, Any], identity_class: str) -> Any:
        value = values.get(identity_class)
        if identity_class == "cloud_account" and isinstance(value, Mapping): value = value.get("account_id")
        if value is None and identity_class == "cloud_account": value = values.get("cloud_account_id", values.get("account_id"))
        if value is None and identity_class in {"project", "repository", "client", "tenant", "branch", "environment", "region", "deployment_target", "service", "database", "domain", "external_integration"}:
            value = values.get(identity_class + "_id", values.get(identity_class))
        if identity_class == "credential_reference" and isinstance(value, (list, tuple)): value = value[0] if value else None
        return value

    @staticmethod
    def _candidates(raw: str, identity_class: str) -> tuple[str, ...]:
        labels = {"cloud_account": ("account", "cloud_account"), "repository": ("repo", "repository"), "deployment_target": ("deployment", "target"), "credential_reference": ("credential",)}
        import re
        result = []
        for label in labels.get(identity_class, (identity_class,)):
            result.extend(re.findall(rf"(?:{label})(?:_id|[- ]id)?\s*[:=]\s*[\"']?([A-Za-z0-9._:/-]+)", raw, re.IGNORECASE))
        return tuple(result)

    @staticmethod
    def _match_class(text: str, identity_class: str) -> bool:
        key = identity_class.replace("cloud_", "")
        return key.split("_")[0].lower() in text.lower() or text.startswith("<") or text.upper().startswith("YOUR") or "replace" in text.lower() or "insert" in text.lower() or "example" in text.lower()

    @staticmethod
    def _scope_mismatch(identity_class: str, observed: str, values: Mapping[str, Any], project: str | None, repository: str | None, environment: str | None) -> bool:
        if identity_class in {"project", "repository", "environment"}:
            return observed not in {str(values.get(identity_class)), project, repository, environment}
        for token in (project, repository, environment):
            if not token:
                continue
            token = str(token).lower()
            base = token.split("-")[0].split("_")[0]
            if token not in observed.lower() and len(base) > 2 and base in observed.lower():
                return True
        return False

    def _receipt(self, run_id: str, work_unit_id: str, raw: str, result: ValidationResult, identity_class: str, expected: Any, observed: Any, reason: str, provenance: Any, context: Mapping[str, Any], surface: str) -> IdentityValidationReceipt:
        timestamp = self.clock()
        material = {"run_id": run_id, "work_unit_id": work_unit_id, "result": result.value, "identity_class": identity_class, "expected": expected, "observed": observed, "reason": reason, "surface": surface}
        validation_id = "validation-" + hashlib.sha256(canonical(material).encode()).hexdigest()[:24]
        sensitive = identity_class in SENSITIVE_IDENTITY_CLASSES
        return IdentityValidationReceipt(run_id, work_unit_id, validation_id, result.value, identity_class, hashlib.sha256(str(expected).encode()).hexdigest()[:40] if expected is not None else None, f"{context.get('context_id', 'context')}:{identity_class}" if expected is not None else None, None if sensitive or observed is None else str(observed), hashlib.sha256(str(observed).encode()).hexdigest()[:40] if observed is not None else None, str(observed) if result == ValidationResult.INVALID_PLACEHOLDER else None, str((context.get("values") or context).get("project", "")), str((context.get("values") or context).get("repository", "")), str((context.get("values") or context).get("environment", "")), str(provenance), reason, surface, timestamp)
