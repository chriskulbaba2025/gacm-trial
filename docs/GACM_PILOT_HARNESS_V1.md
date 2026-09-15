# GACM Pilot Harness v1

Phase 13 composes the proven Phase 1–12 controls into one retry-safe lifecycle. The harness is an orchestration boundary: GitHub authority, Graphify discovery, operational context, model routing, GCU execution, independent verification, repair scope, identity validation, promotion/rollback, and SETTLE retain their own decisions and receipts.

## Lifecycle

`INITIALIZED → AUTHORITY_RESOLVED → CONTEXT_RESOLVED → PLANNED → EXECUTING → VERIFYING → PROMOTION_READY → PROMOTION_PENDING → SETTLE_REQUIRED → SETTLING → COMPLETED`.

Failure branches are `REPAIR_REQUIRED → REPAIRING`, `BLOCKED`, `FAILED`, and `ROLLBACK_REQUIRED`. `PROMOTION_PENDING` is the human gate when configured. Completion is written only after SETTLE passes (or an explicit policy says settlement is not required).

`PilotHarness` receives a `HarnessConfig`, durable `RunStateStore`, and `HarnessAdapters`. Adapters invoke existing subsystem APIs; the harness does not interpret the PRD, qualify models, certify execution, or replace any Phase 9/11/12 state machine.

## Resume, retry, and evidence

`MemoryRunStateStore` is useful for tests; `JsonRunStateStore` reconstructs a run from JSON without chat context. Every transition, subsystem result, receipt, blocker, and assurance-preservation note is append-only in the snapshot. Terminal states are idempotent, completed units are skipped, and deterministic run IDs make infrastructure retries re-load the same logical run. Resume checks the configured project and starting authority and refuses stale authority.

## Repair and human authority

Verification must return an independent `PASS`. A non-pass result is sent to the existing repair-scope adapter; only its affected scope is repaired and reverified. The adapter may report a broader requalification classification; the harness does not widen scope itself. Promotion requires the configured human approval when required; a model or executor cannot manufacture that approval.

## Stop conditions and synthetic paths

The harness fails closed for ambiguous/stale authority, unresolved context, missing model qualification, execution failure, missing or non-independent verification, unresolved repair, blocked promotion, and missing settle/rollback adapters. The deterministic test suite exercises clean pass, local repair, broad requalification, blocked authority/context, model and scope enforcement, verifier self-certification rejection, human promotion gating, durable resume, duplicate retry, and settle failure to rollback. All simulations are in-memory and do not use credentials or modify a real project.
