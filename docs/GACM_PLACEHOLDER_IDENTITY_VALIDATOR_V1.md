# GACM Placeholder and Identity Validator v1

**Phase:** 10 — deterministic placeholder and identity validation
**Module:** `src/gacm/identity_validation/`

## Problem addressed

The validator prevents an executor from emitting placeholders, guessed values,
stale context, or identities belonging to another project, repository, or
environment. A prompt cannot enforce this because the model may omit, invent,
or re-ask for a value; validation therefore occurs as a machine boundary.

## Authoritative identity rules

Only a `VERIFIED`/`RESOLVED` operational-context snapshot supplies expected
values. Context identity and revision may be pinned by the caller, and a stale
snapshot is `BLOCKED`. Chat, model, and memory provenance cannot establish
identity. The active project/repository/environment scope is checked before
output is accepted.

## Placeholder detection and comparison

`PlaceholderPatterns` uses extensible regular expressions for angle-bracket
tokens, `YOUR_*`, replace/insert instructions, synthetic example IDs, and
known-user re-prompts. Structured output is canonicalized to deterministic JSON.
For each required identity class, the authoritative value must be observable;
an alternative parsed value is `INVALID_IDENTITY` or `INVALID_SCOPE`.

## Scope and contamination

Project, repository, and environment are compared directly. Account, tenant,
region, and other values are compared to the verified context and active scope.
Values with another project/environment marker are rejected as cross-project or
cross-environment contamination, even if valid in a different context.

## No-user-reprompt rule

Requests such as “What is your account ID?” or “Enter your region” match the
reprompt patterns and fail as `INVALID_PLACEHOLDER` when the value already
exists in governed context.

## Sensitive values

Receipts retain a context/class reference and SHA-256 digests. Account, tenant,
and credential values are not copied into `observed_value`; placeholder text
may be retained because it is not a secret. The validator never requires
plaintext secret persistence.

## Integration boundaries

The optional GCU adapter hook runs after bounded runner output and before its
receipt reaches independent verification. A non-`VALID` result makes the
executor receipt `FAILED` and preserves the validation receipt as evidence.
Phase 8 remains the only authoritative PASS issuer. Validation failures can be
passed to Phase 9 as the changed local/authority surface; they do not trigger a
full replay without dependency evidence.

`IdentityValidationReceipt.to_run_state_projection()` emits append-only
`IDENTITY_VALIDATION_RECEIPT` evidence and a schema-validated validation record.
