# GACM Execution Authority and Inference State Contract v1

**Status:** PASS — MANDATORY CROSS-CUTTING GOVERNANCE INVARIANT ACCEPTED
**Effective boundary:** Before Foundation 10 and every future governed execution
**Scope:** GACM-wide
**Core principle:** Correct execution must not depend on an executor voluntarily respecting prose instructions.

## Purpose

GACM already governs repository identity, operational context, provider/model authority, writable surfaces, verification, promotion, rollback and SETTLE.

This contract closes a remaining control gap:

A work unit can be fully authorized while still leaving the executor too much discretion over the individual actions it chooses to reach the authorized outcome.

GACM therefore distinguishes design inference from execution authority.

## Core invariant

Unbounded inference is permitted during design.

After an execution recipe is frozen, unbounded inference is revoked.

During governed execution, the executor may act only through:

1. explicitly authorized machine-checkable actions; and
2. explicitly declared bounded-judgment slots.

No other inference creates action authority.

## Canonical authority states

Every governed execution uses one explicit state:

`DESIGN -> FROZEN -> EXECUTION -> VERIFICATION`

Any authority, identity, transition, recipe, or action mismatch moves the execution to:

`BLOCKED`

The executor may not infer its current state.

### DESIGN

Design may explore alternatives, compare approaches, diagnose uncertainty, and propose candidate recipes.

DESIGN does not authorize side effects.

### FROZEN

The selected execution recipe is immutable and identity-stamped.

The frozen recipe defines the action/transition authority for the work unit.

### EXECUTION

Only actions returning machine `ALLOW` from the per-action authority gate may proceed.

Execution inference is limited to declared bounded-judgment slots.

### VERIFICATION

Execution has completed the frozen transition sequence and produced required evidence.

The executor still cannot issue authoritative PASS.

### BLOCKED

Execution stops fail-closed.

No workaround, substitution, alternate tool, provider, command, dependency, target, or recipe edit is implied by the blocked condition.

## Frozen execution recipe

Each execution-ready work unit must carry a `GACM_EXECUTION_RECIPE_V1`.

The recipe must contain:

- recipe ID and version;
- work-unit identity;
- `state = FROZEN`;
- `mutation_policy = GOVERNED_REFREEZE_REQUIRED`;
- ordered steps;
- allowed action kinds;
- allowed tools;
- allowed target patterns;
- parameter constraints;
- acceptable prior states;
- expected result states;
- required evidence;
- STOP conditions;
- bounded-judgment slots.

The recipe identity is SHA-256 over canonical machine-readable content.

A recipe change therefore changes execution-package identity.

## Per-action authorization gate

Every side-effecting or material execution action must be proposed before execution.

The deterministic flow is:

`PROPOSED ACTION -> AUTHORITY CHECK -> ALLOW | DENY`

The authority check compares the proposed action against the current frozen step.

At minimum it checks:

- current execution-authority state;
- recipe digest;
- current step identity;
- action kind;
- tool identity;
- target;
- parameter constraints;
- bounded-judgment slot, if any;
- acceptable prior state.

A denied action moves the gate to `BLOCKED`.

The runner cannot continue by choosing another unapproved action.

Availability never creates authority.

An installed tool, available command, credential, provider, model, package, dependency, environment variable, or workaround is irrelevant unless the current frozen step explicitly authorizes it.

## Transition contract

A recipe does not freeze every future literal runtime value.

It freezes the permitted transition:

`authorized prior state + authorized action + acceptable result state + required evidence -> next recipe step`

This prevents deterministic execution from collapsing into brittle scripting.

After an allowed action, the runner must report:

- action ID;
- result state;
- required evidence references.

The result state must be one of the frozen expected result states.

Missing evidence or an unexpected result state moves execution to `BLOCKED`.

Only a complete recipe sequence may transition to `VERIFICATION`.

## Bounded judgment

Bounded judgment is allowed only when declared in the frozen recipe.

A bounded-judgment slot must define:

- slot ID;
- purpose;
- allowed values;
- `may_expand_scope = false`.

The executor may choose only one allowed value.

A judgment cannot:

- create a new option;
- expand scope;
- change authority;
- change provider/model;
- edit the recipe;
- bypass a STOP condition;
- promote or release;
- convert missing evidence into proof.

Unbounded judgment during EXECUTION is a policy violation and must be denied before the action.

## Recipe mutation

The executor cannot edit its own recipe.

The recipe is canonically frozen before the runner receives it.

If the recipe is wrong or reality invalidates it:

1. execution becomes `BLOCKED`;
2. the discrepancy is preserved as evidence;
3. GACM exits EXECUTION;
4. diagnosis occurs under governed design authority;
5. a revised recipe is explicitly authorized;
6. the revised recipe receives a new digest/package identity;
7. only then may execution resume.

There is no executor-owned â€œsmall fix to the recipe.â€

## Unexpected state

Unexpected state is not workaround authority.

The executor must not silently:

- switch commands;
- change files outside the current action;
- install or change dependencies;
- select another provider/model;
- substitute credentials;
- change environment;
- broaden repair scope;
- alter tests;
- skip steps;
- reorder steps;
- reinterpret STOP conditions.

The correct result is `BLOCKED` with the exact discrepancy.

## Durable state

New graph-bound work units persist an `execution_authority` projection containing:

- state;
- recipe ID;
- recipe version;
- recipe digest;
- mutation policy;
- inference mode.

The execution handoff separately binds:

- `execution_authority_state = EXECUTION`;
- exact frozen recipe digest.

Continuation after process/session/chat loss must reconstruct these values from durable state.

Conversation memory cannot reconstruct or alter execution authority.

## Runner boundary

The GCU execution adapter no longer accepts an unguarded legacy runner.

A runner must implement the guarded interface and receive the `ActionAuthorizationGate`.

A completed runner must have:

- obtained `ALLOW` for its governed action sequence;
- recorded acceptable result transitions;
- supplied evidence;
- completed the recipe into `VERIFICATION`.

Otherwise the execution receipt is BLOCKED or FAILED.

Every run preserves an `ACTION_AUTHORIZATION_RECEIPT` containing:

- recipe digest;
- ALLOW/DENY decisions;
- state transitions;
- evidence references;
- terminal authority state;
- completion flag.

The receipt is executor evidence only. It is not authoritative PASS.

## Relationship to existing controls

This contract strengthens rather than replaces:

- GACM operational-context authority;
- graph-bound work-unit identity;
- provider/model authority;
- credential provenance;
- writable/forbidden surfaces;
- generalized whole-system acceptance;
- independent verification;
- promotion/rollback;
- SETTLE.

Writable scope answers **where** execution may change state.

The execution recipe answers **what action may occur next, using which tool/parameters, from which prior state, with what bounded judgment and evidence**.

Both are required.

## Control-layer rule

This contract adds mandatory control:

`CL-43 â€” EXECUTION AUTHORITY AND INFERENCE STATE`

Prompt-only compliance is insufficient.

Machine enforcement belongs to:

- ORCHESTRATION for freezing recipe/state;
- EXECUTION / GCU boundary for per-action ALLOW/DENY;
- DURABLE AUTHORITY for recipe/state identity;
- INDEPENDENT VERIFICATION for checking resulting evidence and candidate.

## Acceptance requirements

This contract is accepted only when tests prove:

1. frozen recipe is mandatory before graph work reaches execution gate;
2. recipe digest is bound into work-unit/package identity;
3. durable run-state schema can persist recipe/state identity;
4. execution requires explicit `EXECUTION` state;
5. unguarded legacy runner is blocked before invocation;
6. correct in-sequence action returns ALLOW;
7. wrong step returns DENY;
8. wrong tool returns DENY;
9. available-but-unauthorized tool returns DENY;
10. wrong target returns DENY;
11. unexpected parameter returns DENY;
12. unauthorized parameter value returns DENY;
13. unbounded judgment returns DENY;
14. bounded judgment accepts only declared values;
15. missing evidence blocks transition;
16. unexpected result state blocks transition;
17. original recipe mutation after gate creation cannot expand authority;
18. recipe self-mutation policy is rejected;
19. completed execution produces an action-authorization receipt;
20. full GACM governance regression passes;
21. exact candidate CI passes;
22. Foundation 10 remains unopened until this invariant is accepted.

## Non-goals

This contract is not a new RICE subsystem and does not rename existing GACM architecture.

â€œRICEâ€ may remain explanatory shorthand, but the normative GACM concepts are:

- execution authority state;
- frozen execution recipe;
- per-action authorization;
- bounded judgment;
- governed re-freeze.

## Final invariant

A model may recommend an action.

Only GACM authority may permit it.

An executor must never be able to turn its own inference, convenience, availability, or workaround into execution authority.

## Acceptance result

Accepted on implementation candidate:

`8ae0eb6779972d5da0c326e6820f6704aa209877`

Parent authority:

`4d82190d5b7f3bbc187740578bb119f3768f2c33`

Verification evidence:

- targeted execution-authority stack: **85/85 PASS**;
- full GACM governance regression: **258/258 PASS**;
- exact-SHA GitHub CI: **PASS**;
- candidate audit: **18 expected files, zero unexpected files, zero secret literal hits**;
- frozen recipe required before routed graph work reaches the execution gate: **PASS**;
- recipe digest bound to work-unit/package/current-state identity: **PASS**;
- durable run-state execution-authority projection: **PASS**;
- unguarded legacy runner denied before invocation: **PASS**;
- wrong step/tool/target/parameter/judgment controls: **PASS**;
- missing evidence and unexpected result transition fail closed: **PASS**;
- original recipe mutation cannot expand a live authority gate: **PASS**;
- self-mutable recipe policy rejected: **PASS**;
- action-authorization receipt preserved as non-authoritative execution evidence: **PASS**;
- Foundation 10 remained unopened during this correction;
- qualification application repository, Railway staging, application `main`, GACM `main`, and production were not mutated by this correction.

Independent verifier:

`gacm-independent-verifier-v1`

Verification ID:

`verify-4ea554fa7257310fe0a81c03`

Outcome: **authoritative PASS**.

Scope classification: **AUTHORITY_BEARING**. Broader requalification was required and completed by the exact targeted/full-regression/CI/durable-state/negative-path evidence above.

### Acceptance decision

`CL-43 — EXECUTION AUTHORITY AND INFERENCE STATE` is now a permanent mandatory GACM control.

Future governed execution-ready work units must satisfy this contract. Foundation 10 may be opened only after inheriting this invariant; Foundation 10 was not opened by this acceptance.
