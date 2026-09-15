# GACM Settle / Observation Gate v1

## Purpose

Phase 12 prevents a mechanically successful promotion from being treated as stable without bounded, deterministic observation. Phase 11 remains the only promotion and rollback authority.

## Canonical states

`SETTLE_REQUIRED` is emitted by Phase 11 when the promoted candidate requires observation. `OBSERVING` owns an exact settle run. `SETTLE_PASS` and `SETTLE_FAIL` are immutable decision states. `STABLE` is reachable only after `SETTLE_PASS`. `ROLLBACK_REQUIRED` is the governed condition emitted by a failed settle; the existing Phase 11 `ROLLBACK_PENDING` / `ROLLED_BACK` mechanism performs rollback. `BLOCKED` is fail-closed for missing or contradictory identity/evidence.

Legal observation transitions are:

```text
SETTLE_REQUIRED -> OBSERVING -> SETTLE_PASS -> STABLE
                          \-> SETTLE_FAIL -> ROLLBACK_PENDING -> ROLLED_BACK
                          \-> BLOCKED
```

There is no `PROMOTED -> STABLE` transition when observation is required, and no direct `COMPLETE` transition.

## Settle policy

`SettlePolicy` is a deterministic abstraction containing policy identity/version, required and optional check names, a positive bounded observation window, minimum successful observations, and immediate-fail conditions. It does not contain product-specific checks. The caller supplies named check results; the gate validates completeness and governs progression.

## Identity continuity

Entry requires the Phase 11 settle receipt, exact candidate and artifact identities, preserved prior authority, rollback target, and unchanged current authority. Every observation compares the current authoritative identity to the promoted candidate. Drift is recorded as `BLOCKED`; contradictory evidence is not merged.

## Receipts and durable state

Each observation or terminal decision produces an append-only `SettleReceipt` containing the settle run, candidate, artifact, prior authority, promotion receipt, policy identity/version, checks, evidence references, observed authority, timestamps, result, failure reason, rollback target, and next governed action. `to_run_state_projection()` emits `settle`, `settle_history`, and an evidence record without rewriting Phase 1–11 history. The schema accepts the Phase 12 states while retaining prior settle-state compatibility.

## Failure behaviour and rollback integration

Missing required checks, unknown checks, failed checks, immediate-fail conditions, insufficient successful observations, or identity drift fail closed. A `SETTLE_FAIL` receipt preserves all prior promotion and verification references and directs the caller to rollback. Rollback uses Phase 11 `request_rollback` and `execute_rollback`; Phase 12 creates no second rollback mechanism.

## Human authority boundary

Human approval remains a Phase 11 prerequisite for promotion. Deterministic `SETTLE_PASS` may be stabilized automatically after exact authority continuity is rechecked. A model or settle policy cannot authorize promotion or rollback; those actions remain governed by Phase 11 actor checks.

## Historical evidence preservation and idempotency

Promotion, verification, repair, failure, and prior-authority evidence is retained unchanged. Repeating an identical observation returns the original receipt and does not increment the successful-observation count. Terminal states reject further settle execution, preventing duplicate stable transitions or duplicate rollback requirements.
