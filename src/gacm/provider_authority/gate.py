"""Fail-closed external provider authority and credential provenance gate."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Mapping

GATE_ID = "GACM-EXTERNAL-PROVIDER-AUTHORITY-AND-CREDENTIAL-PROVENANCE-GATE"
EXTERNAL_PROVIDER_AUTHORITY_UNDER_SPECIFICATION = "EXTERNAL_PROVIDER_AUTHORITY_UNDER_SPECIFICATION"
CREDENTIAL_PROVENANCE_UNDER_SPECIFICATION = "CREDENTIAL_PROVENANCE_UNDER_SPECIFICATION"
AVAILABLE_BUT_UNAUTHORIZED = "AVAILABLE_BUT_UNAUTHORIZED"

_SECRET_KEYS = {
    "secret", "secret_value", "token", "access_token", "refresh_token",
    "api_key", "password", "private_key", "credential_value",
}

_REQUIRED_AUTHORITY_FIELDS = (
    "provider_id",
    "account_identity",
    "environment",
    "endpoint_identity",
    "credential_source_id",
    "credential_provenance",
    "governing_authority_artifact",
    "authorization_scope",
)


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)


class ExternalProviderGateStatus(StrEnum):
    PASS = "PASS"
    HOLD = "HOLD"


@dataclass(frozen=True)
class ExternalProviderGateResult:
    gate_id: str
    status: str
    reasons: tuple[str, ...]
    identity_digest: str
    provider_id: str | None
    account_identity: str | None
    environment: str | None
    endpoint_identity: str | None
    model_api_variant: str | None
    credential_source_id: str | None
    credential_provenance: str | None
    governing_authority_artifact: str | None
    authorization_scope: str | None
    authoritative: bool
    issuer_role: str = "GACM_GOVERNANCE"

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "status": self.status,
            "reasons": list(self.reasons),
            "identity_digest": self.identity_digest,
            "provider_id": self.provider_id,
            "account_identity": self.account_identity,
            "environment": self.environment,
            "endpoint_identity": self.endpoint_identity,
            "model_api_variant": self.model_api_variant,
            "credential_source_id": self.credential_source_id,
            "credential_provenance": self.credential_provenance,
            "governing_authority_artifact": self.governing_authority_artifact,
            "authorization_scope": self.authorization_scope,
            "authoritative": self.authoritative,
            "issuer_role": self.issuer_role,
        }


class ExternalProviderAuthorityGate:
    """Deterministic gate. It evaluates non-secret identity metadata only."""

    accepted_statuses = {ExternalProviderGateStatus.PASS.value}

    def evaluate(
        self,
        authority: Mapping[str, Any] | None,
        request: Mapping[str, Any] | None,
    ) -> ExternalProviderGateResult:
        authority = dict(authority or {})
        request = dict(request or {})
        reasons: list[str] = []

        if self._contains_secret(authority) or self._contains_secret(request):
            reasons.append("SECRET_MATERIAL_PRESENT_IN_PROVIDER_IDENTITY_RECORD")

        for field in _REQUIRED_AUTHORITY_FIELDS:
            if not authority.get(field):
                if field == "credential_provenance":
                    reasons.append("CREDENTIAL_PROVENANCE_UNPROVEN")
                else:
                    reasons.append("PROVIDER_AUTHORITY_UNPROVEN")

        if authority.get("provider_authority") != "AUTHORIZED":
            reasons.append("PROVIDER_AUTHORITY_UNPROVEN")

        if authority.get("credential_provenance") != "VERIFIED":
            reasons.append("CREDENTIAL_PROVENANCE_UNPROVEN")

        if authority.get("model_variant_required") is True and not authority.get("model_api_variant"):
            reasons.append("MODEL_IDENTITY_MISMATCH")

        self._match(authority, request, "provider_id", "PROVIDER_IDENTITY_MISMATCH", reasons)
        self._match(authority, request, "account_identity", "ACCOUNT_IDENTITY_MISMATCH", reasons)
        self._match(authority, request, "environment", "ACCOUNT_IDENTITY_MISMATCH", reasons)
        self._match(authority, request, "endpoint_identity", "ENDPOINT_IDENTITY_MISMATCH", reasons)
        self._match(authority, request, "credential_source_id", "CREDENTIAL_PROVENANCE_UNPROVEN", reasons)

        if authority.get("model_api_variant") is not None or request.get("model_api_variant") is not None:
            self._match(authority, request, "model_api_variant", "MODEL_IDENTITY_MISMATCH", reasons)

        requested_provider = request.get("provider_id")
        authorized_provider = authority.get("provider_id")
        if requested_provider and authorized_provider and requested_provider != authorized_provider:
            reasons.append("UNAUTHORIZED_PROVIDER_SUBSTITUTION")

        if request.get("substitution_reason") or request.get("api_compatible_substitute") is True:
            if requested_provider != authorized_provider:
                reasons.append("UNAUTHORIZED_PROVIDER_SUBSTITUTION")

        # Discovery is diagnostic only. It never supplies missing authority.
        discovered = request.get("discovered_credentials")
        if discovered and not authority.get("credential_source_id"):
            reasons.append("CREDENTIAL_PROVENANCE_UNPROVEN")

        identity = {
            "provider_id": authority.get("provider_id"),
            "service_id": authority.get("service_id"),
            "account_identity": authority.get("account_identity"),
            "environment": authority.get("environment"),
            "endpoint_identity": authority.get("endpoint_identity"),
            "model_api_variant": authority.get("model_api_variant"),
            "credential_source_id": authority.get("credential_source_id"),
            "credential_provenance": authority.get("credential_provenance"),
            "governing_authority_artifact": authority.get("governing_authority_artifact"),
            "authorization_scope": authority.get("authorization_scope"),
            "candidate_release_sha": authority.get("candidate_release_sha"),
        }
        digest = hashlib.sha256(_canonical(identity).encode()).hexdigest()

        reasons = list(dict.fromkeys(reasons))
        status = ExternalProviderGateStatus.HOLD.value if reasons else ExternalProviderGateStatus.PASS.value
        return ExternalProviderGateResult(
            gate_id=GATE_ID,
            status=status,
            reasons=tuple(reasons),
            identity_digest=digest,
            provider_id=identity["provider_id"],
            account_identity=identity["account_identity"],
            environment=identity["environment"],
            endpoint_identity=identity["endpoint_identity"],
            model_api_variant=identity["model_api_variant"],
            credential_source_id=identity["credential_source_id"],
            credential_provenance=identity["credential_provenance"],
            governing_authority_artifact=identity["governing_authority_artifact"],
            authorization_scope=identity["authorization_scope"],
            authoritative=(status == ExternalProviderGateStatus.PASS.value),
        )

    @staticmethod
    def _match(
        authority: Mapping[str, Any],
        request: Mapping[str, Any],
        field: str,
        reason: str,
        reasons: list[str],
    ) -> None:
        requested = request.get(field)
        authorized = authority.get(field)
        if requested is not None and authorized is not None and requested != authorized:
            reasons.append(reason)

    @classmethod
    def _contains_secret(cls, value: Any) -> bool:
        if isinstance(value, Mapping):
            for key, item in value.items():
                if str(key).lower() in _SECRET_KEYS and item not in (None, "", "<REDACTED>", "REDACTED"):
                    return True
                if cls._contains_secret(item):
                    return True
        elif isinstance(value, (list, tuple)):
            return any(cls._contains_secret(item) for item in value)
        return False
