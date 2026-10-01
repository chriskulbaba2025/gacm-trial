# GACM External Provider Authority and Credential Provenance Gate v1

## Authority

Gate ID:

`GACM-EXTERNAL-PROVIDER-AUTHORITY-AND-CREDENTIAL-PROVENANCE-GATE`

This is a mandatory fail-closed governance control before any authenticated external action.

Permanent generalized failure patterns:

- `EXTERNAL_PROVIDER_AUTHORITY_UNDER_SPECIFICATION`
- `CREDENTIAL_PROVENANCE_UNDER_SPECIFICATION`

The control is universal. It is not tied to any one product, provider, model, cloud, deployment platform, payment service, email service, data service, database, automation service, or historical incident.

## Problem prevented

A governed executor may discover a usable provider, SDK, account, credential, endpoint, model or compatible API and infer that it is authorized.

That inference is prohibited.

An internally self-consistent provider configuration can still be unauthorized.

Core invariant:

> AN AVAILABLE CREDENTIAL IS NOT AUTHORITY.
>
> AN AVAILABLE PROVIDER IS NOT AUTHORITY.
>
> API COMPATIBILITY IS NOT AUTHORITY.
>
> A SELF-CONSISTENT MANIFEST IS NOT AUTHORITY.

Discovery and authority are distinct states:

`DISCOVERED != AUTHORIZED`

A discovered credential or provider may be recorded as `AVAILABLE_BUT_UNAUTHORIZED` until governing provenance is proven.

## Scope

This gate applies before authenticated external execution involving, including but not limited to:

- LLM/model providers;
- cloud platforms;
- payment providers;
- email providers;
- analytics providers;
- search/data providers;
- storage providers;
- deployment platforms;
- SaaS APIs;
- databases;
- external automation systems;
- any authenticated third-party service.

## Required proof before network execution

Before the first authenticated external request, GACM must prove:

1. which provider/service is authorized;
2. which account/project/tenant/environment is authorized;
3. which endpoint is authorized;
4. which model/product/API variant is authorized where applicable;
5. which credential source belongs to that provider/product/environment;
6. which governing artifact authorized that identity.

If any required element is unresolved, the governed action is HOLD before network execution.

## Provider authority

Provider identity must be named or deterministically derived from authoritative project configuration.

Permitted authority sources include:

- accepted project configuration;
- governed provider manifest;
- approved architecture decision;
- authoritative environment mapping;
- explicitly approved deployment configuration.

The following are discovery evidence only and are never sufficient authority:

- a global environment variable exists;
- a CLI is authenticated;
- an SDK is installed;
- another project uses the provider;
- an API is compatible;
- a provider is cheaper;
- a provider is popular;
- a worker already knows how to use it;
- a provider or model happens to be available.

## Credential provenance

Every credential used for governed external execution must have non-secret provenance proving that it belongs to:

- the governed product/project;
- the selected provider/service;
- the intended environment;
- the selected account/project/tenant where relevant;
- the authorized scope.

A globally available credential must never be repurposed automatically.

Examples:

- `ANTHROPIC_AUTH_TOKEN` does not authorize Anthropic for an unrelated product.
- `OPENAI_API_KEY` does not authorize OpenAI merely because it exists.
- an authenticated AWS profile does not authorize mutation of every AWS-backed project.
- a Vercel login does not authorize deployment of every accessible project.

## No provider substitution

If the governed provider is unavailable:

`STATUS = HOLD`

The executor must not silently substitute:

- another model provider;
- an API-compatible proxy;
- a cheaper provider;
- a provider with available credentials;
- a personally authenticated account;
- a fallback account.

Provider substitution requires explicit governed authority.

## Authority before parity

Required ordering:

`PROVIDER AUTHORITY → CREDENTIAL PROVENANCE → ENDPOINT/MODEL IDENTITY → MANIFEST IDENTITY → RUNTIME PARITY → COST/POLICY GATES → EXTERNAL EXECUTION`

A later parity/currentness check cannot legitimize an unauthorized upstream choice.

## Cost authorization separation

Permission to spend money is not provider authorization.

A paid-call authorization permits spend only inside an already governed provider/service identity and scope.

It does not permit the executor to choose any paid provider available on the machine.

## Required non-secret identity record

Where applicable, every governed external-provider action records:

- `provider_id`;
- `service_id`;
- account/project/tenant identifier;
- environment;
- endpoint identity;
- model/API version;
- credential source identifier;
- credential provenance classification;
- governing authority artifact;
- candidate/release SHA;
- authorization scope;
- timestamp.

Secret values must never be recorded.

## Fail-closed statuses

The gate must be able to return:

- `PROVIDER_AUTHORITY_UNPROVEN`;
- `CREDENTIAL_PROVENANCE_UNPROVEN`;
- `PROVIDER_IDENTITY_MISMATCH`;
- `ENDPOINT_IDENTITY_MISMATCH`;
- `MODEL_IDENTITY_MISMATCH`;
- `ACCOUNT_IDENTITY_MISMATCH`;
- `UNAUTHORIZED_PROVIDER_SUBSTITUTION`.

All prevent the authenticated external action.

## Discovery boundary

Provider/credential discovery may be used for diagnosis.

Discovery never mutates the governed configuration automatically.

A discovered candidate remains non-authoritative until the project/provider/account/environment provenance chain is proven.

## Handoff and restart

Provider authority must persist through handoff, restart and currentness verification.

A new worker/process may not re-discover credentials and silently select a different provider/account.

Durable state must preserve non-secret provider authority metadata and the governing authority reference.

## Generalized regression requirements

Acceptance requires tests proving:

1. unknown provider fails before network execution;
2. available but unauthorized credential fails;
3. correct provider with wrong credential provenance fails;
4. correct provider with wrong endpoint fails;
5. correct provider with unauthorized model/API variant fails;
6. multiple discovered credentials do not trigger automatic provider selection;
7. API-compatible substitute provider fails;
8. matching manifest/runtime cannot override missing provider authority;
9. spend authorization cannot override provider authority;
10. correct explicitly authorized provider/configuration proceeds;
11. secrets are not written to logs/proofs/state;
12. provider authority survives handoff/restart/currentness verification.

Adversarial cases must include:

- unrelated global token;
- alternate compatible provider;
- multiple provider credentials;
- matching unauthorized manifest/runtime;
- cheaper substitute;
- unavailable approved provider;
- stale provider configuration;
- wrong account/environment.

## Promotion and release interaction

This gate executes before external execution.

Release-currentness and parity gates remain necessary later, but cannot repair missing upstream provider authority.

Promotion eligibility must fail if a required external-provider action lacks authoritative provider and credential-provenance evidence.

## Generalization rule

Every future governed product involving an authenticated external service must automatically evaluate this gate.

The gate belongs before execution, not as post-failure diagnosis.

The two failure patterns are reusable GACM governance patterns and must remain in the permanent regression library.

## Work-unit classification control

A governed execution policy that enables this gate must require every work unit to declare whether it performs an authenticated external action.

Missing classification is HOLD.

A work unit declared non-external must fail before execution if the routing layer introduces a provider, endpoint or credential-source identity.

This prevents omission of the external-action flag from becoming a bypass.

