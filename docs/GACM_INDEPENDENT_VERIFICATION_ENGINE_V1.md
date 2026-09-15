# GACM Independent Verification Engine v1

## Verification authority

Phase 8 is the independent verification boundary. Execution produces evidence;
this engine decides whether that evidence is sufficient for the authorized
work-unit contract. Only a receipt issued by `IndependentVerificationEngine`
with status `PASS`, issuer role `INDEPENDENT_VERIFIER`, and `authoritative=true`
may project authoritative PASS into durable run state.

Executor receipts are inputs, never decisions. An executor receipt that claims
authoritative PASS or includes executor-issued verification PASS is rejected.

## Independence boundary

The engine receives the run-state snapshot, work-unit contract, executor receipt,
independent starting/ending repository identities, independently observed changed
paths and diff evidence, test contract/results, operational-context identity,
routing decision, and prior assurance records. It compares these observations
itself. It does not accept an executor's changed-file list as the source of
truth, although disagreement with that list is preserved as a failure reason.

The caller may obtain changed paths from Git using a separate read-only adapter;
`actual_changed_paths` is deliberately distinct from `execution_receipt.files_changed`.
If the independent observation is unavailable, the result is `UNOBSERVABLE`,
not PASS.

## Deterministic checks

The engine checks:

- run and work-unit identity;
- starting repository SHA, repository identity, branch, and worktree;
- ending repository SHA, repository identity, branch, and worktree;
- executor receipt identity and status;
- independently observed diff paths against allowed and forbidden surfaces;
- executor changed-path claims against independent paths;
- required test outcomes against the test contract;
- expected outcome result;
- operational-context snapshot identity and revision;
- routing decision, selected model, and qualification identity;
- executor self-certification claims;
- availability of diff evidence and independent observations.

Missing critical evidence produces `UNOBSERVABLE`. Proven mismatches or policy
violations produce `FAIL`. Missing or contradictory governed preconditions can
produce `BLOCKED`. No status is promoted to PASS by inference.

## Repair-scope classification

The deterministic scope layer classifies the independently observed changed paths
as:

- `LOCAL` — affected-scope verification only; unrelated assurance is preserved.
- `DEPENDENCY_EXPANDED` — dependent scope and affected assurance must be rerun.
- `AUTHORITY_BEARING` — authority-dependent assurance is invalidated and authority
  revalidation is required.
- `MODEL_BEARING` — model-dependent assurance is invalidated and model
  requalification is required.
- `ARCHITECTURE_BEARING` — architecture-dependent assurance is invalidated and
  broader requalification is required.
- `UNKNOWN` — blast radius cannot be determined; the engine blocks rather than
  guessing.

Classification precedence is authority, model, architecture, dependency, local.
The execution model cannot choose or override this classification.

## Assurance preservation and invalidation

Each prior assurance record identifies surfaces, dependency classes, and rerun
scope. For `LOCAL`, only records whose surfaces intersect the changed paths are
invalidated; unrelated prior PASS evidence remains preserved. Dependency,
authority, model, and architecture classifications invalidate the corresponding
dependent records and emit the rerun scope. `UNKNOWN` invalidates assurance for
the purpose of continuation and requires requalification evidence.

The engine emits these decisions as evidence. It does not silently trigger the
later repair or requalification machinery.

## Durable-state integration

`VerificationReceipt.to_run_state_projection()` emits an
`INDEPENDENT_VERIFICATION_RECEIPT` evidence item and a Phase 2-compatible work
unit update. PASS projects to work-unit `PASS` with authoritative independent
verification. FAIL, BLOCKED, and UNOBSERVABLE project non-PASS states. The
projection is validated against `schemas/gacm-run-state.schema.json` in tests.

## Why executor self-certification is prohibited

The executor controls neither independent observation nor final authority. It
can omit a changed file, misstate a test result, use a different model, or claim
PASS despite a scope violation. Independent repository identity, diff, test,
context, and routing checks prevent those claims from becoming authoritative.

## Phase boundary

This phase implements deterministic verification only. It does not implement
model-assisted judging, promotion, rollback orchestration, repair execution,
SETTLE, or Phase 9 dependency-logic orchestration. Any condition requiring
unavailable semantic or model judgment remains explicit evidence for a later
governed decision rather than an implicit PASS.
