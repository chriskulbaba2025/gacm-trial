# GACM Repair-Scope / Dependency Engine v1

**Phase:** 9 — deterministic repair-scope and dependency logic
**Module:** `src/gacm/repair/`

## Purpose

The engine calculates the smallest proven verification scope after a failure or
repair. A changed surface invalidates only assurance that depends on it. The
engine emits a plan; it does not execute repair, verify behavior, or issue an
authoritative PASS.

## Dependency authority

Work-unit dependency IDs in the governed run-state contract and corroborated
Git/GitHub or approved durable-state relationships are authoritative inputs.
Graphify can discover candidate relationships, but a Graphify-only claim is
ignored. A Graphify relationship becomes usable only when the input explicitly
includes corroborating governed evidence. Model-generated claims are likewise
non-authoritative without governed corroboration.

## Classifications and closure

Classification is deterministically derived from independently observed changed
paths and surface flags, in this order: `AUTHORITY_BEARING`, `MODEL_BEARING`,
`ARCHITECTURE_BEARING`, `DEPENDENCY_EXPANDED`, `LOCAL`, `UNKNOWN`. Direct units
are those whose governed allowed surfaces match. The reverse dependency graph is
then traversed in sorted order to compute transitive dependents.

`LOCAL` invalidates only the directly affected assurance. Dependency-expanded
repairs invalidate the direct unit and its dependent closure. Authority/model /
architecture changes invalidate only assurance marked as depending on that
category, plus units in the proven closure.

## Assurance and historical PASS

Plans separately report `assurance_invalidated` and `assurance_preserved`.
Historical PASS receipt IDs are retained in `historical_pass_receipts`; an
invalidated receipt is not deleted or rewritten. `currently_reliable_assurance`
contains only preserved assurance that may still support continuation.

## Requalification and full replay

Authority changes require authority revalidation; model changes require model
requalification; architecture changes require broader architecture
requalification. A full replay is required only when the proven affected closure
covers every governed unit, an applicable all-scope trigger is proven, or scope
evidence is insufficient to bound the impact. “Safer to rerun everything” is not
a decision rule. Unknown scope returns `BLOCKED_FOR_SCOPE_RESOLUTION`.

## Verifier and executor relationship

The verifier receipt is consumed as an observation and cross-checked against
governed paths. An executor’s claimed repair classification or changed scope
cannot override the calculated plan. The plan cannot issue or project an
authoritative PASS; only the Phase 8 independent verifier may do that.

## Durable-state integration

`RepairPlan.to_run_state_projection()` emits an append-only
`REPAIR_SCOPE_PLAN` evidence item and the complete plan. A consumer appends it
to `repair_plans` and preserves the original verification receipt/evidence.
