# GACM Jev Classification and Graph Binding v1

**Status:** IMPLEMENTATION CANDIDATE
**Authorized:** 2026-10-03
**Starting authority:** `150f895f4effa74dee116d51dd7fbee974445447`

## Purpose

Use cheap semantic classification to reduce unnecessary generative reasoning while preserving GACM authority, evidence, and execution controls.

The operating pattern is:

`RAW STATE → FIXED JEV CLASSIFICATION → NON-AUTHORITATIVE GRAPH CANDIDATE → EVIDENCE COLLECTION → GOVERNED GRAPH STATE → DETERMINISTIC SCHEDULING → GRAPH-BOUND EXECUTION CONTRACT`

Jev is a classifier/filter. It is not a workflow engine, verifier, release authority, model router, or decision authority.

## Jev boundary

The runtime boundary is `src/gacm/classification/`.

The default requested TypeSafe model is `jev-latest`.

The API credential is read from `JEV_API_KEY` at runtime. The key must never be committed, serialized into run state, written into proof artifacts, or included in graph payloads.

The client records non-secret reproducibility metadata:

- requested model;
- resolved model returned by TypeSafe;
- fixed question set;
- returned answers and probabilities;
- input/output token counts;
- request digest;
- result digest.

The provider response is treated as untrusted input. Choice labels must exist in the requested fixed taxonomy, confidence/probabilities must be valid, and probability keys must match the requested criteria.

## Deterministic taxonomy

Jev selects codes. GACM code owns titles and graph types.

Initial intake taxonomy:

- `DEFECT` → `Defect`;
- `EVIDENCE_GAP` → `Evidence Gap`;
- `REQUIREMENT` → `Requirement`;
- `CONSTRAINT` → `Constraint`;
- `DEPENDENCY` → `Dependency`;
- `RISK` → `Risk`;
- `UNKNOWN` → `Unknown`.

Jev may not generate a new category or title at runtime.

## Epistemic restriction

A Jev classification may enter the governed graph only as:

`INFERRED | HYPOTHESIS`

It may never enter as:

`EVIDENCED | ACCEPTED`

The candidate has no authority reference and is marked not verified.

`GraphScheduler` converts inferred/hypothesis candidates into `COLLECT_EVIDENCE` work before they can govern a repair, gate, or release decision.

Confidence is metadata only. A high Jev probability never becomes authority.

## Routing authority

The automatic execution route is GPT-5.6 Luna only.

If Luna does not satisfy the assessed capability envelope, routing returns:

`HUMAN_MODEL_AUTHORIZATION_REQUIRED`

GACM does not automatically choose Terra, Sol, or another model.

A non-Luna route requires a durable `ModelAuthorization` containing:

- authorization ID;
- work-unit ID;
- exact model ID;
- human authority reference;
- actor ID;
- authorization timestamp.

The GCU boundary rechecks that authority before execution.

## Graph-to-execution binding

A graph-derived work package is not executable merely because it contains a task.

`GraphWorkPackageBinder` binds the exact machine state into `WorkUnitContract`:

- graph action ID;
- graph revision;
- target object ID;
- project ID;
- routing decision ID;
- selected model;
- qualification identity;
- explicit external-action classification;
- allowed/forbidden surfaces;
- test contract;
- STOP conditions;
- rollback authority.

GCU preconditions compare the contract to the current graph identity. A mismatch in action, revision, target, project, route, repository identity, branch, worktree, context, or starting SHA blocks execution.

Because graph identity is part of the machine policy, a graph revision change also changes execution package identity.

## External action rule

Live Jev inference is an external provider action.

A production/runtime integration must therefore use the existing GACM external-provider-authority and credential-provenance controls before authenticated network execution. Ambient discovery of `JEV_API_KEY` proves only that a credential exists; it does not itself authorize TypeSafe/Jev as a provider for a governed run.

## Currentness limitation

TypeSafe currently exposes `jev-latest` as a model alias. This tranche records the requested and resolved model strings plus request/result digests. If TypeSafe exposes a durable immutable model/version identity, a future hardening tranche should bind it into provider-currentness evidence.

## Acceptance

This tranche is acceptable only if proof shows:

- Jev cannot create evidenced/accepted graph truth;
- labels outside the fixed taxonomy fail closed;
- invalid confidence/probability responses fail closed;
- inferred classifier candidates schedule evidence collection;
- Luna remains the only automatic route;
- non-Luna routing/escalation requires explicit durable human authority;
- graph action/revision identity survives into run state and GCU machine policy;
- stale or mismatched graph identity blocks execution;
- route identity mismatch blocks execution;
- subagents remain unauthorized by default;
- external-action classification remains explicit;
- full pre-existing GACM regression remains PASS.

## Explicit exclusions

This tranche does not:

- make Jev authoritative;
- fine-tune a classifier;
- create a training-data pipeline;
- replace GraphScheduler with Jev;
- replace PilotHarness planning/lifecycle;
- persist the governed graph across process restart;
- add vector retrieval or convergence;
- merge or deploy to production.

Verified human/independent-verifier corrections may later become labelled training data, but self-generated unverified classifications must never train the future classifier as truth.
