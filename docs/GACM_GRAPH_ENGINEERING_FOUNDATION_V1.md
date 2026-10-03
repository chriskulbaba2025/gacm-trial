# GACM Graph Engineering Foundation v1

**Status:** IMPLEMENTATION CANDIDATE
**Authorized:** 2026-10-03
**Starting authority:** `0dd82e6176bd00e32fddfc975584a70773350b14`

## Purpose

Move GACM from prompt-sequenced orchestration toward graph-engineered orchestration.

The graph determines what exists, what depends on what, what is unresolved, what is eligible to run, and what evidence is required.

Prompts become bounded renderings of machine state. They do not define workflow authority.

## Core invariant

`GOVERNED GRAPH STATE → DETERMINISTIC ELIGIBILITY → BOUNDED WORK PACKAGE → OPTIONAL MODEL REASONING → EVIDENCE → VALIDATED GRAPH MUTATION`

Not:

`PROMPT → MODEL DECIDES WHAT TO DO NEXT → NEXT PROMPT`

## Authority separation

The graph does not replace existing GACM authorities.

- Git/GitHub remains source and release identity authority.
- Approved durable artifacts remain contract authority.
- Run state remains operational lifecycle authority.
- Independent verification remains authoritative verification.
- Human authority remains required for governed human decisions.
- Graphify remains discovery-only.
- The governed graph stores durable reasoning objects and relationships.
- LLMs may reason over bounded graph context and propose mutations.
- LLMs may not directly write authoritative graph truth.

## Runtime package

Foundation module:

`src/gacm/graph/`

It contains:

- `models.py` — typed graph objects, epistemic states, relationship vocabulary, mutation and receipt contracts;
- `store.py` — revisioned mutation validation and current graph projection;
- `persistence.py` — atomic durable graph persistence, replay reconstruction, stale-writer control and cross-process writer locking;
- `scheduler.py` — deterministic next-action and work-package planning;
- `binder.py` — graph-action/revision binding into GCU `WorkUnitContract`;
- `__init__.py` — public graph API.

The advisory classifier boundary lives separately in `src/gacm/classification/` so semantic classification cannot become graph authority by module placement.

## Governed object model

Nodes include the V2 architecture's durable reasoning classes:

- Requirement;
- BusinessGoal;
- UserNeed;
- Assumption;
- Unknown;
- Evidence;
- EvidenceGap;
- Decision;
- Constraint;
- Risk;
- Dependency;
- Defect;
- RootCause;
- FailurePattern;
- Change;
- Test;
- Gate;
- Artifact;
- System;
- Component;
- Contract;
- StateTransition;
- Tranche;
- HumanApproval;
- ReleaseIdentity.

Edges use a governed vocabulary including:

- DEPENDS_ON;
- AFFECTS;
- VERIFIED_BY;
- SUPPORTS;
- CONTRADICTS;
- OBSERVED_IN;
- POSSIBLY_CAUSED_BY;
- MAY_SHARE_CAUSE_WITH;
- EXPLAINS;
- ADDRESSES;
- REQUIRES;
- DETECTED;
- BLOCKED_BY;
- SUPERSEDES;
- BASED_ON;
- IMPLEMENTS.

Workers may not invent relationship types outside the governed enum.

## Epistemic model

Every node and edge has an epistemic state:

`USER_STATED | OBSERVED | EVIDENCED | INFERRED | HYPOTHESIS | CONFLICTED | ACCEPTED | SUPERSEDED | UNKNOWN`

Confidence is metadata, not authority.

`EVIDENCED` and `ACCEPTED` require an authority reference and digest.

Discovery cannot create evidenced or accepted truth.

Executor output cannot create evidenced or accepted truth.

Accepted truth requires governed human, governance, or release authority.

## Provenance/currentness fields

Graph nodes and edges carry:

- project and optional organization/run scope;
- source and source snapshot;
- provenance references;
- authority reference and digest;
- producer role;
- verification state;
- confidence;
- created/valid time fields;
- supersession target;
- schema version;
- typed payload.

These fields exist so a graph assertion can be reconstructed and invalidated without chat memory.

## Mutation contract

Every graph change is a `GraphMutation`.

Required controls:

- exact expected graph revision;
- immutable mutation ID;
- project scope;
- authenticated actor role;
- idempotency key;
- evidence and authority references;
- append-only mutation history;
- resulting revision receipt.

The runtime rejects:

- stale writes;
- replay-key collisions;
- cross-project edges;
- missing endpoints;
- unsupported relationship types;
- illegal epistemic regressions;
- missing provenance;
- unbound superseded state;
- invalid confidence;
- unauthorized authoritative writes.

Exact mutation replay is idempotent and does not create another revision.

## Deterministic scheduler

`GraphScheduler` derives eligible work from graph state.

Current deterministic priority:

1. resolve conflicted state;
2. close evidence gaps;
3. diagnose defects lacking evidenced/accepted root cause;
4. collect evidence for unknown/inferred/hypothesis state;
5. run eligible gates;
6. verify requirements;
7. request required human approval;
8. execute eligible tranches.

A blocked gate is not scheduled until its graph blockers are resolved.

A tranche is not scheduled until its governed dependencies and blockers resolve.

This ordering is machine logic, not prompt wording.

## Work-package projection

The scheduler emits bounded work-package data.

The package carries:

- graph action ID;
- graph revision;
- target object;
- objective;
- allowed and forbidden surfaces;
- test contract;
- stop conditions;
- authority references;
- model-routing identity;
- external-action classification;
- subagent authorization;
- model-escalation authorization.

The scheduler does not render a model prompt.

A separate execution adapter may render a prompt only after the machine package passes authority gates.

## Model and agent controls

A model name alone is not routing authority.

Execution readiness requires:

- selected model;
- qualification identity;
- routing decision ID.

If any is absent:

`STATUS = READY_FOR_ROUTING`

The scheduler does not substitute a model.

For the current governed operating policy, GPT-5.6 Luna is the default external Codex execution model. A route still requires its governed routing identity.

Work packages default fail-closed to:

- `subagents_authorized = false`;
- `model_escalation_authorized = false`.

These may become true only through explicit governed authorization.

No scheduler logic creates Luna → Terra → Sol escalation.

### Routing authority reconciliation

Graph Foundation 02 resolves the legacy automatic-routing HOLD.

The `src/gacm/routing/` boundary now enforces:

- GPT-5.6 Luna is the only automatic/default execution-model route;
- if Luna does not satisfy the assessed capability envelope, routing returns `HUMAN_MODEL_AUTHORIZATION_REQUIRED` rather than choosing Terra or Sol;
- every non-Luna route requires a durable explicit `ModelAuthorization` naming the work unit and model;
- escalation requires the same explicit human authority and cannot be inferred from risk;
- routing decisions retain selected model, qualification identity, routing decision ID, and human authority reference where applicable;
- an execution-model string supplied by an executor remains non-authoritative.

The graph-to-GCU binder independently rechecks these identities and rejects a non-Luna route without the durable human authorization fields.

## External-action control

Every executable work package must explicitly classify:

`external_action_required = true | false`

Missing classification produces:

`HOLD_MISSING_EXTERNAL_ACTION_CLASSIFICATION`

This prevents provider/credential use from appearing later as an implicit executor choice.

## Relationship to existing repair graph

`WorkUnitDependencyGraph` in `src/gacm/repair/` remains valid for repair assurance calculations.

The new governed graph is the broader reasoning/control graph.

Repair dependency evidence should later be projected from accepted governed graph edges rather than maintaining an independent manually assembled relationship source.

That integration is not part of this tranche.

## Relationship to PilotHarness

`PilotHarness` remains the accepted lifecycle implementation. Graph Foundation 03B integrates `GraphScheduler` at the planning boundary without rewriting authority, execution, verification, repair, generalization, promotion, SETTLE, or rollback ownership.

Planning authority is explicit:

- omitted or `LEGACY_ADAPTER` keeps the existing procedural planner unchanged;
- `GRAPH_SCHEDULER` requires an injected `GraphScheduler` and makes graph-derived eligibility the executable unit source;
- the legacy planner still runs in graph mode only as a non-authoritative shadow and cannot add, remove, reorder, or broaden executable graph work;
- any graph revision change caused by the shadow planner fails closed;
- graph HOLD packages fail before routing;
- any eligible graph `HUMAN_APPROVAL` action fails closed rather than falling back to legacy work;
- graph revision and eligible action identities are frozen as planning evidence and rechecked before execution, after routing, and on resumed PLANNED state;
- route receipts must name the exact graph-selected work unit;
- a graph package with pre-bound model/qualification/routing identity cannot be silently replaced by the routing adapter;
- non-secret external-provider request identity is carried from graph payload into the bounded work package so the existing external-provider authority gates remain active.

The graph mode does not render prompts. Prompts remain downstream bounded renderings of machine state.

The migration path is:

1. graph kernel and deterministic scheduler — completed in Graph Foundation 01;
2. graph-to-run-state / graph-to-GCU binder plus routing authority reconciliation — completed in Graph Foundation 02;
3. graph scheduler to PilotHarness planning integration — implemented additively in Graph Foundation 03B;
4. durable graph persistence/reconstruction;
5. graph-aware CRIT questioning;
6. bounded retrieval;
7. convergence/shared-root detection;
8. independently verified graph-derived release acceptance.

The legacy planner is not removed by Foundation 03B. Existing accepted controls remain active until the graph-derived path is independently accepted.

## What prompts are still allowed to do

Prompts may:

- explain a bounded objective to a model;
- provide selected graph context;
- request diagnosis, transformation, implementation, or critique;
- request structured proposed mutations or evidence.

Prompts may not:

- create authority;
- change graph revision;
- select new scope;
- decide the next tranche;
- override blockers;
- select an unauthorized provider/model;
- authorize escalation;
- spawn agents;
- issue authoritative PASS;
- promote or release.

## Foundation acceptance

This foundation is acceptable only if tests prove:

- graph revision enforcement;
- replay/idempotency protection;
- project isolation;
- endpoint validation;
- provenance and authority requirements;
- discovery/executor authority restrictions;
- epistemic transition enforcement;
- deterministic dependency traversal;
- deterministic scheduler ordering;
- gate/tranche eligibility from graph state;
- stale graph actions are rejected;
- model name alone is insufficient routing authority;
- external-action classification fails closed;
- subagents and model escalation default false.

## Explicit exclusions

This foundation does not implement:

- PostgreSQL/pgvector or Neo4j;
- vector/lexical retrieval;
- graph-aware CRIT;
- convergence detection;
- cross-project generalized learning;
- application/runtime staging integration of the durable store;
- production graph migration;
- production deployment.

Those require separate governed tranches.

## Durable persistence / reconstruction

Graph Foundation 04 implements the durable graph contract defined in `docs/GACM_GRAPH_DURABLE_PERSISTENCE_V1.md`.

The durable store:

- persists the full graph snapshot, mutation history and mutation receipts;
- reconstructs only by replaying governed mutations through `GovernedGraph.apply()`;
- cross-checks the replayed projection and receipts before returning a graph;
- rebuilds idempotency state through replay;
- uses exact-revision compare-and-swap checks so stale writers fail closed;
- rejects divergent durable history;
- uses a cross-process non-blocking OS writer lock;
- writes by same-directory temporary file plus atomic replacement;
- replay-validates candidate graph state before persisting it;
- preserves GraphScheduler action identity across restart for the same graph revision.

The persistence artifact and payload digest are integrity/currentness mechanisms only. They do not create epistemic, human, verification, provider, model or release authority.

## Next owning boundary

After Graph Foundation 04 is independently accepted, application/runtime wiring of the durable graph into the actual GACM app and staging/browser path should be a separate governed tranche.

That tranche must not silently combine runtime wiring with retrieval, graph-aware CRIT, convergence, cross-project learning, legacy-planner removal, broad V2 migration, or production promotion.
