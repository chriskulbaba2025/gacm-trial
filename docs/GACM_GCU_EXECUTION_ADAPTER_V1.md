# GACM GCU Execution Adapter v1

## Purpose and boundary

The Phase 7 adapter is the deterministic boundary between GACM orchestration and
GCU/Codex. GACM authorizes a bounded work unit; GCU executes that package and
returns evidence. The adapter does not move authority into the executor, model,
prompt, or Graphify.

The governing rule is:

> GCU executes the authorized work unit. GACM retains authority over scope,
> model, operational context, verification boundaries, and durable run state.

Hermes and independent verification are outside this phase.

## Preconditions

`GCUExecutionAdapter.prepare()` returns `BLOCKED` unless all of these are true:

- GitHub authority is `VERIFIED` and its repository, branch, worktree, and HEAD
  match the work-unit contract.
- Operational context is `VERIFIED` and its immutable snapshot identity and
  revision match the work unit.
- The durable work unit is `READY`.
- A routing decision exists and its selected model and qualification identity
  match the contract; the model is qualified.
- Allowed writable surfaces and forbidden surfaces are explicit.
- Rollback authority is present.
- The observed starting HEAD, branch, worktree, and clean state match the
  authorized starting state.

The adapter never asks the executor to repair a missing authority value.

## Machine-readable contract and rendering

`WorkUnitContract` contains the run and unit identities, objective, expected
outcome, authorized starting SHA, branch/worktree, context snapshot, selected
model and qualification, writable policy, test/evidence contracts, STOP rules,
dependencies, and broader-requalification triggers.

`ExecutionRequest.machine_policy()` is the authoritative structured package.
The rendered prompt is derived from that policy for GCU/Codex usability. It
explicitly states that the prompt cannot expand scope, change the model, resolve
authority, or declare PASS. A future executor may replace the renderer while
consuming the same machine contract.

Identical request inputs produce the same package identity.

## Writable-surface enforcement

After execution, every changed path is checked against the explicit allowed and
forbidden patterns. A forbidden or unauthorized path changes the receipt to
`FAILED`; the changed paths and evidence are preserved. The adapter never
silently expands the allowed set and does not rely on prompt compliance.

The executor cannot change the selected model: if it reports a different model,
the receipt is `FAILED`. It cannot create a new route or qualification.

## Starting-state enforcement

Immediately before the runner is called, an optional `GitExecutionStateReader`
can read the checked-out HEAD, branch, worktree, and clean state directly from
Git. Any mismatch blocks the runner invocation. The caller must supply the
corresponding authoritative values in the request; chat or model memory is not
accepted as a substitute.

## Receipt and post-execution evidence

`ExecutionReceipt` records:

- run, work-unit, and execution identities;
- starting and ending SHA;
- model and qualification identity;
- changed files, commands, tests, outcomes, artifacts, and diff summary;
- executor status (`COMPLETED`, `FAILED`, `BLOCKED`, or `STOPPED`);
- timestamps, claimed affected scope, and STOP/BLOCKED reason;
- deterministic authority/model/architecture surface flags.

The adapter reports evidence; it does not determine final repair scope or
requalification. Surface flags identify evidence that the later verification
and dependency layer must evaluate. A local change therefore does not itself
invalidate unrelated prior PASS evidence. A changed shared authority, model,
architecture, schema, security, or verification surface is flagged for the
broader requalification logic that follows in later phases.

## Durable-state integration

`ExecutionReceipt.to_run_state_projection()` creates an executor evidence record
and a work-unit projection with status `VERIFYING` for a completed execution.
Its verification status is `NOT_RUN`, `authoritative` is `false`, and issuer role
is `EXECUTOR`. Failed executions project as failed evidence. The projection is
compatible with the Phase 2 evidence/work-unit structures and cannot write
authoritative `PASS`.

Only independent verification may write authoritative PASS, as required by the
Phase 1 control-layer audit and the Phase 2 schema.

## Future executor portability

The adapter accepts a callable runner that consumes an `ExecutionPackage` and
returns `RunnerResult`. This isolates Codex/GCU invocation details from GACM
policy and receipts. Hermes or another executor can implement the same boundary
without acquiring authority, routing, verification, promotion, or release
permissions.
