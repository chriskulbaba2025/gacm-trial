# GACM Pilot v1 Durable Run-State Contract

**Contract:** `gacm-run-state.schema.json`
**Version:** 1.0.0
**Phase:** 2 — Durable Run-State Schema
**Canonical format:** JSON Schema draft 2020-12

## Purpose

This contract is the durable reconstruction record for one GACM run. It allows a new process, chat, session, or model to resume from repository-backed state rather than conversation memory. It records the exact candidate, authority references, work-unit boundaries, execution evidence, verification decisions, repair scope, promotion/deployment identity, SETTLE result, rollback authority, and terminal stop reason.

The schema is a snapshot contract. It validates the shape and local consistency of one snapshot. It does not by itself provide storage, locking, append-only history, authorization, dependency analysis, or a complete transition-history proof. Those are runtime invariants described below.

## Control-layer alignment

The contract implements the Phase 1 placement without moving ownership:

| Contract area | Audit ownership | Relevant controls |
|---|---|---|
| Repository, PRD, GACM, Graphify provenance | DURABLE AUTHORITY | CL-01–03, CL-31, CL-41 |
| Operational context and identity fields | DURABLE AUTHORITY + ORCHESTRATION | CL-04–17, CL-33 |
| Work-unit boundary and dependencies | ORCHESTRATION, with discovery evidence | CL-21–27 |
| Model and qualification receipt | ORCHESTRATION | CL-18–20 |
| Executor output and evidence | EXECUTION / GCU | CL-21–23 |
| Verification decision and authoritative PASS | INDEPENDENT VERIFICATION | CL-28–30 |
| Promotion, deployment, SETTLE, rollback | RELEASE / SETTLE + HUMAN JUDGMENT where required | CL-34–39 |

The schema never makes Graphify authoritative and never gives an executor permission to write an authoritative PASS.

## Top-level fields

| Field | Meaning | Authority / mutability |
|---|---|---|
| `schema_version`, `state_type` | Contract identity and discriminator. | GOVERNANCE; immutable for a record. |
| `run_id` | Stable identifier for the run. | ORCHESTRATION creates; immutable. |
| `project_id` | Authoritative project identity. | DURABLE AUTHORITY; immutable for a run. |
| `authoritative_start_sha` | Known-good starting candidate. | DURABLE AUTHORITY; immutable. |
| `current_repository_sha` | Exact repository candidate represented by the snapshot. | ORCHESTRATION records after Git resolution; changes only through a governed candidate transition. |
| `repository` | Repository ID, remote, branch, worktree, and protected rollback SHA. | DURABLE AUTHORITY / ORCHESTRATION; identity fields immutable; candidate-related values update only through governed transitions. |
| `prd` | PRD identity and content digest used by the run. | DURABLE AUTHORITY; immutable. |
| `gacm` | Methodology, pilot, and schema release identities. | GOVERNANCE; immutable for the run. |
| `graphify` | Discovery index identity and its authoritative source provenance. | DISCOVERY / GRAPH supplies discovery identity; DURABLE AUTHORITY validates source authority; immutable per indexed snapshot. |
| `operational_context` | Exactly one resolved context, or a blocked/missing context before sensitive work. Includes account, tenant, client, project, repository, branch, environment, cloud account, region, deployment target, and credential references. | ORCHESTRATION resolves; DURABLE AUTHORITY supplies authoritative values; immutable per work unit unless a governed re-resolution creates a new revision. |
| `work_units` | Bounded task records and their dependency edges. | ORCHESTRATION freezes; execution may append evidence and status receipts only within permission. |
| `lifecycle` | Current run state and last transition snapshot. | ORCHESTRATION owns transitions; verifier/release authority may authorize specific transitions but cannot bypass the state machine. |
| `promotion` | Promotion intent, human approval, candidate, and receipt. | RELEASE / SETTLE; human approval is explicit where required. |
| `deployment` | Deployed target and participating revisions. | RELEASE / SETTLE; populated only when deployment exists. |
| `settle` | Released-behavior observation state. | RELEASE / SETTLE; completion is not valid before required `SETTLED`. |
| `rollback_target` | Durable known-good target and authority receipt. | DURABLE AUTHORITY / RELEASE; required for `ROLLED_BACK`. |
| `human_interventions` | Explicit human decisions and scope. | HUMAN JUDGMENT writes only its own authenticated decision record. |
| `timestamps` | Creation, update, execution, and completion times. | ORCHESTRATION records; append-only history is runtime-required. |
| `terminal_stop` | Typed reason and message for a terminal or blocked stop. | ORCHESTRATION records; executor may propose evidence but cannot silently clear it. |
| `evidence` | Content-digested evidence receipts and producer role. | Each producer may append its own evidence; independent verification decides authoritative verification status. |

## Work-unit fields

Each work unit requires `unit_id`, title, dependency IDs, allowed writable surfaces, selected model and qualification identity, status, verification, input/output evidence references, failures, repair attempts, affected scope, and broader-requalification triggers.

`dependencies` are IDs, not a claim that the model’s graph is authoritative. The dependency/blast-radius owner must preserve the source and decision evidence in the referenced evidence records. A work unit may not be considered safely isolated merely because its list is short.

`model.qualification_id` identifies the qualification decision; `model.model_id`, `provider`, and route reason identify what was selected. The model itself does not write or approve its qualification.

## Enumerated states

### Run lifecycle

```text
CREATED → READY → RUNNING → VERIFYING → PROMOTION_PENDING → SETTLING → COMPLETE
```

Failure, blocking, and rollback branches are explicit:

```text
CREATED → BLOCKED / FAILED
READY → BLOCKED
RUNNING → BLOCKED / FAILED
VERIFYING → BLOCKED / FAILED
PROMOTION_PENDING → BLOCKED / FAILED / ROLLED_BACK
SETTLING → BLOCKED / FAILED / ROLLED_BACK
FAILED → BLOCKED / ROLLED_BACK
BLOCKED → READY / FAILED / ROLLED_BACK
```

The schema validates the `lifecycle.last_transition` pair against this allowed edge set. Runtime persistence must validate the entire prior history, actor authorization, monotonic timestamps, candidate identity, and side-effect receipts. A single snapshot cannot prove that history.

### Work-unit lifecycle

The allowed work-unit states are:

```text
PENDING, READY, RUNNING, VERIFYING, PASS, FAIL, BLOCKED, REPAIRING, INVALIDATED
```

The schema requires a verification object for every work unit. A `PASS` work unit must have `verification.status = PASS`, `authoritative = true`, and `issuer_role = INDEPENDENT_VERIFIER`. An executor-authored verification can never be PASS in this contract.

Runtime must additionally validate legal work-unit transitions, dependency readiness, and invalidation of downstream units.

### Verification status

```text
NOT_RUN, PASS, FAIL, BLOCKED, UNOBSERVABLE
```

Only `INDEPENDENT_VERIFIER` may issue an authoritative PASS. `EXECUTOR` is structurally prohibited from combining `issuer_role = EXECUTOR` with `status = PASS` or `authoritative = true`. Runtime authorization must also authenticate the writer and prevent an executor from impersonating the verifier role.

### SETTLE state

```text
SETTLING, SETTLED, FAILED, UNOBSERVABLE, NOT_REQUIRED
```

Where settlement is required, `RUNNING` or `PROMOTION_PENDING` cannot become durable `COMPLETE` until the release/settle owner records `SETTLED` with the observed deployment identity and evidence.

## Immutable and mutable data

### Immutable after run creation

- `schema_version`, `state_type`, `run_id`, `project_id`.
- `authoritative_start_sha`, PRD identity/digest, GACM methodology/pilot identity.
- The initial rollback authority and protected stable target.
- A work unit’s identity, declared dependency IDs, and allowed surfaces once execution starts.
- Historical evidence records, failure records, repair attempts, human interventions, and transition records.

### Mutable only through governed state transitions

- `current_repository_sha` when a candidate is intentionally created and recorded.
- Operational context revision, only after a new authoritative resolution and impact requalification.
- Run and work-unit statuses.
- Promotion, deployment, SETTLE, and rollback state.
- Append-only evidence references and completion timestamps.

### Writer permissions

| Writer | Permitted writes | Prohibited writes |
|---|---|---|
| DURABLE AUTHORITY adapter | Repository/PRD/GACM/rollback identity and authoritative context receipts | Graph-only facts, model qualification, verification PASS |
| ORCHESTRATION | Run/unit creation, lifecycle transitions, context binding, routing receipt, repair classification, state assembly | Independent PASS, human approval impersonation, silent history rewrite |
| EXECUTION / GCU | Execution evidence, output evidence, failure proposal, bounded repair evidence within granted scope | Authority changes, lifecycle promotion, authoritative PASS, rollback waiver |
| INDEPENDENT VERIFICATION | Verification status and authoritative PASS/FAIL/BLOCKED/UNOBSERVABLE evidence | Candidate mutation, scope expansion, human approval |
| RELEASE / SETTLE | Promotion/deployment/settlement/rollback receipts | Rewriting source authority or verifier evidence |
| HUMAN JUDGMENT | Explicit approval, rejection, stop, or risk decision within scope | Editing machine-derived identity or pretending to be an automated verifier |

These are ownership rules, not permissions granted by JSON alone. The runtime must enforce authenticated writer roles and append-only history.

## Repair and assurance invalidation

### Local repair

A `LOCAL` repair records the smallest affected scope and has `broader_requalification_required = false` with no broader trigger. It may invalidate the failed unit and dependent assurance while leaving independent, unaffected prior PASS states valid. Runtime must calculate dependency closure and record the exact re-verification set; the executor cannot choose this classification alone.

The repair sequence is:

```text
FAIL → scoped diagnosis → REPAIRING → affected unit/dependents VERIFYING → PASS or FAIL/BLOCKED
```

### Broader requalification

A `BROADER_REQUALIFICATION` repair requires at least one typed trigger: architecture, shared authority, model-bearing behavior, global configuration, shared schema, security boundary, verification infrastructure, or high-blast-radius dependency. Previous assurance outside the directly changed scope is marked `INVALIDATED` or otherwise excluded from the current release proof by runtime policy. A new independent verification cycle must re-establish assurance before promotion.

The schema checks the classification/trigger relationship. Runtime must determine triggers from dependency and blast-radius evidence and must invalidate stale proof when the candidate or relevant contract changes.

## Rollback representation

`ROLLED_BACK` requires `rollback_target.target_sha`, its durable `authority_source`, and a human-readable reason. The target is the known-good stable identity, not a model suggestion or an inferred parent. The rollback operation and result must be recorded as immutable evidence and the run must retain the failed candidate for reconstruction.

Rollback may be reached from promotion pending, settling, failed, or blocked states. It does not convert the failed candidate into a successful run; it records recovery to a known-good target.

## Continuation after chat/session loss

1. Load the durable snapshot by `run_id` from approved durable state.
2. Verify the repository HEAD, PRD digest, schema version, and current candidate identity.
3. Verify the latest append-only transition/evidence history and writer authorization.
4. Reconstruct the operational context from its authoritative source and compare the context revision/digest.
5. Resume only from a legal state and unexpired unit contract. Chat memory is advisory and cannot fill missing fields.
6. If identity, history, authority, or evidence is missing/ambiguous/stale, write a durable `BLOCKED` or terminal stop reason and do not guess.

This is why the state contains both identity fields and evidence references rather than a conversational summary.

## JSON Schema limits and runtime invariants

The schema intentionally does not claim to enforce what JSON Schema cannot prove:

- It cannot authenticate who wrote a field or prevent a malicious writer from labeling itself `INDEPENDENT_VERIFIER`.
- It cannot prove a full historical transition sequence from one snapshot.
- It cannot calculate dependency closure or blast radius.
- It cannot prove that a SHA is the checked-out Git HEAD, that a Graphify fact resolves to GitHub, or that deployment identity matches the candidate.
- It cannot provide locking, append-only storage, replay protection, or exactly-once state transitions.
- It cannot prove that a referenced evidence ID exists in the durable evidence store.

Those are required runtime controls owned by the layers identified in the Phase 1 audit. A schema-valid document is therefore necessary but not sufficient for a GACM run to proceed or for any release claim.


## Generalization and whole-system gate — schema release 1.1.0

New governed product-repair run states must use `gacm.schema_release = "1.1.0"` and persist both `generalization_contract` and `generalization_gate`.

The contract is frozen before execution and identifies the product-level definition of done, authorized capability scope, connected-system path, required full-path boundaries, fresh-scenario minimum, reference regressions, and continuity/security controls.

The gate result is a governance-issued projection derived from raw independent-verifier evidence. A schema-release 1.1.0 run cannot validate as COMPLETE unless the gate status is `PASS` or `AUTHORIZED_FIXTURE_SPECIFIC`, the result is authoritative, and the issuer role is `GACM_GOVERNANCE`.

Raw proof remains in append-only evidence referenced by the gate result. The executor cannot make the durable state acceptable by writing a PASS string into the snapshot; runtime promotion re-evaluates the raw contract and raw independent evidence.

Historical schema-release states remain historical evidence. Resuming unfinished governed repair under the corrected control requires the new gate rather than silently continuing under fixture-only acceptance.
