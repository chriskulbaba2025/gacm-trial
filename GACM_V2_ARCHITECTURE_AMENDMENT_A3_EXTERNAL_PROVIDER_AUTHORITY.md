# GACM V2 — Architecture Amendment A3: External Provider Authority and Credential Provenance

Status: **ADDITIVE FROZEN ARCHITECTURE AMENDMENT**

Authority: explicit human owner authorization on 2026-09-30.

This amendment preserves the existing GACM V2 architecture and adds one universal fail-closed authority boundary.

## New mandatory gate

`GACM-EXTERNAL-PROVIDER-AUTHORITY-AND-CREDENTIAL-PROVENANCE-GATE`

## Permanent failure patterns

- `EXTERNAL_PROVIDER_AUTHORITY_UNDER_SPECIFICATION`
- `CREDENTIAL_PROVENANCE_UNDER_SPECIFICATION`

## Architectural invariant

Availability, compatibility, parity and cost permission do not establish authority.

Before the first authenticated external request, the governed system must prove provider/service, account/project/tenant/environment, endpoint, model/product/API variant where applicable, credential-source provenance, governing authority artifact and authorization scope.

Discovery is diagnostic only.

`DISCOVERED != AUTHORIZED`

A provider or credential discovered from machine/global state may remain `AVAILABLE_BUT_UNAUTHORIZED`; it may not become configuration without governed provenance.

## Required control ordering

`PROVIDER AUTHORITY → CREDENTIAL PROVENANCE → ENDPOINT/MODEL IDENTITY → MANIFEST IDENTITY → RUNTIME PARITY → COST/POLICY GATES → EXTERNAL EXECUTION`

Later internal consistency cannot legitimize an unauthorized provider selected upstream.

## No substitution

Unavailable authorized provider = HOLD.

No automatic substitution to another provider, API-compatible proxy, cheaper provider, personal account, fallback account or credential discovered from another project.

Substitution requires explicit governed authority.

## Authority interaction

This gate extends, and executes before, Release Currentness and Identity.

Release parity proves that the runtime matches the accepted provider identity. It does not choose or authorize that identity.

Paid-call authorization remains separate from provider authorization.

## Durable state and handoff

Non-secret provider authority metadata and its governing authority reference are part of durable run/handoff state.

A restarted worker must reuse the governed identity or HOLD. It must not rediscover and reselect a provider from ambient credentials.

## Generalization

The rule applies to all authenticated third-party services including model, cloud, deployment, storage, database, payment, email, analytics, search/data, SaaS and automation providers.

No product-specific exception is permitted.

## Acceptance

This amendment is complete only when the gate is documented, represented in run-state contracts, machine-enforced before external execution, re-evaluated before promotion where applicable, included in regression/adversarial testing, and persisted through restart/currentness verification.
