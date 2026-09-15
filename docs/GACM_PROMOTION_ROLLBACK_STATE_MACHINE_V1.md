# GACM Promotion / Rollback State Machine v1

**Phase:** 11 — Promotion / Rollback State Machine
**Module:** `src/gacm/promotion/`

## Purpose and authority boundary

Independent verification establishes candidate assurance; it does not make the
candidate authoritative. `PromotionRollbackStateMachine` is the governance
boundary that evaluates eligibility, records promotion intent, promotes only
after continuity checks, and returns to an explicitly known-good target when
required. Executor and independent-verifier roles are rejected as mutation
actors.

## Eligibility

Eligibility requires verified GitHub authority and operational context,
completed execution, `VALID` placeholder/identity validation, an authoritative
independent-verifier `PASS`, no unresolved blocked state, completed repair and
requalification, exact candidate/artifact identity, an exact rollback target,
current-authority continuity, and configured human approval. Missing conditions
produce `NOT_ELIGIBLE`; unresolved or changed authority produces `BLOCKED`.

## Promotion intent and promotion

`create_promotion_intent()` creates a deterministic, durable-state-compatible
intent receipt in `PROMOTION_PENDING` before authority mutation. `promote()`
requires the exact authority identity captured by the intent. It records both
the prior and promoted identity. Promotion with required observation enters
`SETTLE_REQUIRED`; Phase 11 cannot mark a run `COMPLETE`.

## Rollback

Rollback requires an explicit target present in the governed known-good target
set and an exact current authoritative identity. It transitions through
`ROLLBACK_PENDING` and then `ROLLED_BACK`; arbitrary or unknown targets are
blocked. Promotion, verification, failure, and repair evidence are preserved.
Rollback is not a history rewrite.

## Durable history

Promotion and rollback receipts project append-only evidence plus
`promotion_history`/`rollback_history` records into the Phase 2 run-state
schema. The existing authoritative identity and verification receipts remain
available for reconstruction. No deployment is performed in Phase 11.

## Repair-scope preservation

Promotion and rollback do not erase unrelated assurance. The state machine
records identity and event history only; Phase 9 remains responsible for
changed-surface invalidation and bounded re-verification.

## Phase boundary

`SETTLE_REQUIRED` is an explicit handoff to Phase 12. This implementation does
not observe a released system, perform production deployment, or claim final
release completion.
