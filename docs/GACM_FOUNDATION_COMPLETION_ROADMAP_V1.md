# GACM Foundation Completion Roadmap v1

**Status:** FROZEN ROADMAP CANDIDATE
**Effective:** 2026-10-04
**Authority parent:** `8133ff42c7f29f4e8468bd43a97160a7abb6db23`
**Current accepted capability boundary:** Graph Foundation 12
**Foundation endpoint:** Graph Foundation 18
**Purpose:** Freeze the remaining foundation sequence and the definition of Foundation Complete so the target cannot expand by inference.

## 1. Authority reviewed before freeze

This roadmap was reconciled against the current accepted Foundation 12 state and the existing GACM design authorities, including:

- `GACM_IMPLEMENTATION_PRD_V1.0.md`;
- `GACM_V2_PRODUCT_ARCHITECTURE_ROADMAP.md`;
- `GACM_V2_GOVERNED_CHANGE_INTELLIGENCE_GRAPH.md`;
- `GACM_V2_FINAL_ARCHITECTURE_HARDENING_AUDIT.md`;
- `docs/GACM_PILOT_HARNESS_V1.md`;
- `docs/GACM_MVP_CLOSURE_CONTRACT_V1.md`;
- `docs/GACM_MVP_FINAL_CLOSURE_V1.md`;
- accepted Graph Foundation 01â€“12 contracts and current-state evidence.

Historical contracts remain evidence of what each tranche authorized and proved. Where an older roadmap sentence says a capability is â€œnot yet implementedâ€ but a later accepted Foundation record proves that it was implemented, the later accepted record and current state govern present status.

## 2. Governing rule

Foundation 01 through Foundation 12 remain accepted historical authority and are not reopened by this roadmap.

The remaining foundation sequence is fixed as:

`FOUNDATION 13 -> FOUNDATION 14 -> FOUNDATION 15 -> FOUNDATION 16 -> FOUNDATION 17 -> FOUNDATION 18 -> FOUNDATION COMPLETE`

There is no implied Foundation 19.

A later discovery may not add, split, rename, widen or reorder a foundation stage merely because it appears useful. A roadmap amendment requires explicit human authority and must prove that the proposed change is necessary to satisfy the frozen Foundation Complete definition rather than being productization, optimization, convenience or adjacent capability.

## 3. Foundation Complete definition

GACM reaches **FOUNDATION COMPLETE** only when one governed harness can take an approved change objective from durable authority through planning, authorized execution, verification, bounded repair, requalification, human intervention where required, recovery/resume, currentness and final acceptance without relying on chat memory or permitting the executor to create its own authority.

The complete foundation must prove all of the following:

1. durable authority, project, run, work-unit, tranche, graph, evidence, provider/model and artifact identities;
2. deterministic separation of proposal, approval, execution authority, evidence and authoritative acceptance;
3. graph-governed planning from current human-approved product truth;
4. graph-aware repair planning from failed verification without automatic scope widening;
5. graph identity/conflict/epistemic controls strong enough that graph inference cannot silently become authority;
6. human-approved candidate tranche to frozen execution-recipe binding;
7. per-material-action execution authorization through the existing CL-43 authority gate;
8. bounded repair with affected-scope reverification and broader requalification when prior assurance is invalidated;
9. maximum-repair/reset rules enforced by the harness rather than remembered by the model;
10. exact currentness from source through CI, deployment, served runtime and browser where applicable;
11. durable recovery across process/chat/session interruption;
12. a governed human-intervention protocol for approval, user input, error and completion states;
13. replay-safe and duplicate-safe remote control/notification handling;
14. project isolation and no cross-project truth contamination;
15. provider/model/credential provenance and spend authority where external calls are used;
16. independent verification on the exact candidate and on gate-relevant graph assertions;
17. generalized proof that the harness is not fixture-specific, project-specific or hard-wired to one executor implementation;
18. rollback or explicit non-reversible-action handling;
19. a complete evidence/receipt trail sufficient to reconstruct why the run was allowed, what happened and why it passed or stopped;
20. measurable evidence that graph intelligence adds useful decision/defect-prevention value without increasing governance escapes;
21. production remains a separately authorized boundary;
22. all foundation-critical defects are closed or explicitly classified HOLD.

## 4. Fixed remaining sequence

### Foundation 13 â€” Graph-Aware Repair Planning and Graph Integrity Preconditions

**Objective:** Convert a verified FAIL/HOLD requiring repair into a bounded, evidence-linked candidate repair plan without executing the repair, while closing the graph-integrity gaps that become material once graph reasoning can influence repair scope.

Required flow:

`VERIFICATION FAILURE + CURRENT GRAPH + CURRENT EVIDENCE + HISTORICAL GENERALIZED PATTERNS -> GOVERNED REPAIR PROJECTION -> CANDIDATE REPAIR TRANCHE`

Required repair-planning controls:

- bind the failed verification receipt and exact candidate identity;
- identify root cause, owning boundary, related failure modes and blast radius;
- use convergence/dependency information without turning inference into proven truth;
- historical generalized patterns remain advisory and cannot become current-project evidence;
- compute the smallest affected repair scope;
- preserve inherited forbidden surfaces;
- preserve provider/model/tool restrictions;
- record repair-attempt count and prior failed approaches;
- identify which prior assurances would be invalidated by the proposed repair;
- generate a candidate repair tranche with objective, allowed surfaces, forbidden surfaces, test contract, stop conditions, rollback/irreversibility classification and evidence requirements;
- require human review when existing authority requires it;
- keep `execution_authorized = false`.

Graph-integrity preconditions required before graph-derived repair scope may govern action:

- canonical durable object identity with aliases/duplicate candidates and governed reversible merge/split proposals; a model cannot silently merge identities;
- explicit conflict sets and evidence-lineage/dependence so copied or derived evidence is not counted as independent corroboration;
- epistemic path composition exposing the weakest material link; chained hypotheses/inferences cannot gain authority by accumulation;
- operational-state/graph consistency using shared transaction where possible or a durable outbox/event-ledger plus idempotent reconciliation; material split-brain is HOLD;
- retrieval negative semantics: `NO_MATCH != ABSENT`; approximate or bounded retrieval cannot close an evidence gap by omission;
- mutation impact classes sufficient to distinguish low, material and high-authority graph changes;
- model-assisted assertion provenance sufficient to bind task/contract, model route, provider/model, instruction/template digest, structured-output schema, retrieval receipt and input/output digests without storing private chain-of-thought;
- gate-relevant graph assertions and repair-scope claims are independently verifiable from durable evidence.

Acceptance requires stale graph, cross-project graph, missing verification identity, unsupported causal certainty, unresolved material conflict, operational/graph split-brain, retrieval-miss-as-absence, scope widening and malformed repair history to fail closed.

**Explicitly excluded:** repair execution, automatic approval, production mutation, autonomous methodology change, automatic cross-project learning writes.

### Foundation 14 â€” Governed Candidate-Tranche Execution Bridge

**Objective:** Allow an explicitly approved candidate tranche to enter the existing PilotHarness/GCU execution path without allowing planning output to create execution authority.

Required flow:

`HUMAN-APPROVED TRANCHE -> FROZEN EXECUTION RECIPE -> CL-43 PER-ACTION AUTHORITY -> EXECUTOR/GCU -> EVIDENCE`

Required controls:

- exact tranche identity and approval identity are bound before execution;
- execution recipe digest is frozen and cannot be edited by the executor;
- every material action receives deterministic ALLOW/DENY;
- provider, model, credential provenance, spend authority and operational-context identity are rechecked at the action boundary where applicable;
- forbidden surfaces remain inherited and machine-enforced;
- irreversible/external side effects require explicit pre-action authority and are not automatically retried;
- no subagent, extra model session, provider substitution or model escalation without explicit authority;
- no execution from `READY_FOR_HUMAN_TRANCHE_REVIEW` alone;
- dual-planner ambiguity is eliminated: graph-approved planning is authoritative in graph-governed execution mode, while any legacy planner is isolated behind explicit compatibility mode and cannot silently add, remove, reorder or broaden executable work;
- restart/resume preserves the exact recipe, tranche and action-receipt identities;
- execution evidence records the exact graph/retrieval/reasoning identities that materially informed the authorized work.

**Explicitly excluded:** autonomous repair loop and production promotion.

### Foundation 15 â€” Governed Repair, Reverification and Requalification Loop

**Objective:** Close the controlled failure-to-repair loop under durable harness state.

Required flow:

`VERIFY FAIL -> F13 REPAIR PLAN -> REQUIRED APPROVAL -> F14 EXECUTION -> TARGETED TESTS -> ASSURANCE INVALIDATION ANALYSIS -> AFFECTED-SCOPE REVERIFICATION -> BROADER REQUALIFICATION IF REQUIRED -> INDEPENDENT VERIFY`

Required controls:

- repair only the generic owning boundary;
- preserve the frozen product-level definition of done;
- reference fixtures remain regression evidence only;
- no silent adjacent-work absorption;
- maximum three failed repairs in one defect family, followed by mandatory diagnosis reset;
- prior assurances are explicitly preserved or invalidated;
- architecture-, authority-, model-, security-, schema-, verification- and high-blast-radius changes trigger broader requalification as required;
- successful independent units are not rerun without a dependency reason;
- failure, HOLD, UNOBSERVABLE and PASS remain distinct;
- partial execution/recovery preserves enough state to determine safe resume versus rollback/replan;
- executor cannot certify its own authoritative PASS;
- repair completion cannot silently write a generalized cross-project pattern; any reusable learning remains separately governed.

Acceptance includes clean repair, failed repair, three-repair reset, broad requalification, stale receipt, scope-escape and rollback/stop negative paths.

**Explicitly excluded:** generalized remote-control transport and production promotion.

### Foundation 16 â€” Durable Runtime Control and Human Intervention Protocol

**Objective:** Make long-running GACM execution safely supervisable without requiring a human to watch the chat.

Canonical intervention states:

`RUNNING | NEEDS_APPROVAL | NEEDS_USER | ERROR | DONE | BLOCKED`

Required controls:

- intervention state is durable harness state, not inferred only from chat text;
- one active execution lease/owner per run where material actions are possible;
- restart after process/browser/chat loss reconstructs the current authorized checkpoint;
- duplicate resume/approve commands are idempotent;
- stale or replayed approvals fail closed;
- approver identity and approval scope are recorded;
- remote commands cannot create authority beyond the current governed transition;
- notifications contain no secrets;
- a durable outbox/retry mechanism prevents transient notification failure from losing a required intervention;
- routine expected progress does not notify by default;
- ERROR, NEEDS_APPROVAL, NEEDS_USER and DONE can emit governed events;
- transport adapters cannot reinterpret governance state;
- an orphaned executor/process can be distinguished from a legitimately running unit before a replacement execution lease is issued;
- external side-effect actions are protected against duplicate replay after transport/process interruption.

Telegram/n8n may be one adapter, but Telegram is not the authority layer. The protocol must remain transport-neutral so another UI, API, Slack, email or control console can be added later without changing governance semantics.

**Explicitly excluded:** general chat-over-Telegram as a product feature, enterprise SSO/RBAC suite, production mutation.

### Foundation 17 â€” Whole-Harness Generalization, Value and Adversarial Qualification

**Objective:** Prove that the completed harness is genuinely general and beneficial rather than a successful path for one project, fixture, graph configuration or executor implementation.

Minimum qualification:

- at least two materially different governed project/change scenarios;
- strong, mixed and weak/ambiguous input conditions where applicable;
- fresh inputs not used to shape implementation;
- cross-project isolation;
- one real executor path plus an independently substitutable adapter/contract path sufficient to prove the harness is not hard-coded to one executor;
- interrupted execution and durable resume;
- duplicate/replayed event and approval negative controls;
- stale source/deployment/runtime identity negative controls;
- unauthorized provider/model/credential negative controls;
- forbidden production-action negative control;
- attempted scope widening negative control;
- attempted self-approval/self-verification negative control;
- failure-pattern retrieval without truth contamination;
- convergence inference without causal overclaim;
- explicit convergence false-positive tests using superficially similar but materially unrelated defects;
- retrieval tests proving misses are not treated as absence and tenant/project filters do not leak evidence;
- exact release-currentness and real runtime/browser proof where applicable;
- controlled graph-value comparison on fresh scenarios, comparing governed graph intelligence with an appropriate non-graph/control path and measuring material issues found/missed, useful/redundant questions, unsupported assumptions, convergence accuracy, repair cycles, requirement/evidence coverage and governance escapes;
- context/token volume, external-call count, latency, cost and human-intervention measurements are recorded; budget pressure may remove optional enrichment but cannot weaken mandatory authority/evidence/verification gates.

A second paid commercial executor is not required for Foundation Complete unless a future explicit amendment proves it is necessary; executor-neutrality may be proven through the stable adapter contract plus independent substitute implementation.

**Explicitly excluded:** universal support for every agent/provider, commercial-scale load testing, broad enterprise deployment.

### Foundation 18 â€” Foundation Closure and Harness v1 Freeze

**Objective:** Add no new product capability. Audit and close the frozen foundation as one system.

Required closure sequence:

`AUTHORITY AUDIT -> WHOLE-SYSTEM MAP -> FINAL DEFECT REGISTER -> ROOT-CAUSE REVIEW -> REQUIRED REPAIRS ONLY -> TARGETED TESTS -> FULL REGRESSION -> GENERALIZATION/VALUE GATE -> CURRENTNESS -> REAL RUNTIME/BROWSER -> RECOVERY/INTERVENTION TEST -> FINAL ADVERSARIAL AUDIT -> INDEPENDENT VERIFICATION -> FOUNDATION FREEZE`

Foundation 18 must prove:

- Foundations 01â€“17 remain intact on one exact candidate or on an explicitly reconciled authority set;
- no unresolved foundation-critical defect;
- all historical/current roadmap contradictions are reconciled;
- exact source/CI/deployment/runtime identity where applicable;
- durable run reconstruction without chat memory;
- complete evidence manifest;
- all forbidden surfaces preserved;
- production untouched unless a separate explicit production authority exists;
- independent verifier returns authoritative PASS;
- final governance regression and exact-SHA governance CI pass;
- final status is written as `FOUNDATION_COMPLETE`.

If any required proof is unavailable, Foundation 18 is HOLD. It may repair only defects required by this frozen definition of done. It may not add new capabilities.

## 5. Frozen post-foundation work

The following are explicitly **post-foundation** unless a future explicit roadmap amendment proves they are required to satisfy Section 3:

- production deployment/promotion;
- customer-facing commercial rollout;
- multi-tenant SaaS packaging;
- full enterprise RBAC/SSO administration;
- billing/subscription systems;
- polished commercial dashboard/UI;
- ongoing portfolio-health/management dashboards and recurring MRR product features;
- support for every LLM, coding agent, cloud or deployment provider;
- a second paid commercial executor solely for marketing breadth;
- Neo4j or another graph database;
- vector/embedding retrieval unless separately justified;
- autonomous cross-project learning or automatic rule promotion;
- autonomous methodology/governance rewriting;
- model training or weight modification;
- Hermes, Paperclip, Laya or other worker/classifier integration merely because available;
- generalized conversational Telegram operation beyond governed intervention/control;
- broad analytics/BI features;
- production-grade retention/deletion/legal-hold implementation beyond what is needed to keep foundation test data safe;
- production disaster-recovery/point-in-time-restore program;
- production schema/index/embedding migration program;
- governance-repository branch protection/ruleset hardening when not required for the isolated foundation candidate;
- commercial-scale performance/load engineering;
- optimization work that does not close a frozen acceptance defect.

These items may become later productization, scale, enterprise, integration, ongoing-management or production-hardening programs. Their absence does not prevent `FOUNDATION_COMPLETE`.

## 6. Roadmap change control

The roadmap is deliberately fail-closed against moving goalposts.

A newly discovered item may enter the frozen foundation only when **all** are true:

1. evidence proves the item blocks at least one Section 3 Foundation Complete requirement;
2. the blocker cannot be safely deferred to post-foundation work;
3. the owning boundary is identified;
4. adding or changing the stage is explicitly authorized by a human;
5. the roadmap receives a new version and durable acceptance identity.

Otherwise the item is recorded as deferred and the fixed Foundation 13â€“18 sequence remains unchanged.

A model, executor, verifier, graph, historical pattern, test failure or implementation convenience cannot create Foundation 19.

## 7. Audit findings that caused this freeze

The pre-freeze audit identified these structural risks:

1. **No fixed post-Foundation-12 endpoint.** This allowed the finish line to expand as each next capability was discovered. Resolved by Foundation 18 as the fixed closure stage.
2. **Foundation 12 plans but cannot execute.** Candidate tranche output is explicitly non-executable. Foundation 14 owns the execution bridge.
3. **Repair planning remained explicitly deferred.** Foundation 13 owns this gap.
4. **The existing repair-scope machinery was not yet closed into the graph-governed execution loop.** Foundation 15 owns end-to-end repair, assurance invalidation and requalification.
5. **Remote notification existed as an operational convenience, not as a governed runtime protocol.** Foundation 16 separates durable intervention semantics from Telegram/n8n transport.
6. **A single successful project path would be insufficient evidence for a general harness claim.** Foundation 17 owns cross-project and executor-neutrality qualification.
7. **There was no final post-graph closure gate preventing additional foundations from being invented during acceptance.** Foundation 18 is capability-free closure and explicitly prohibits inferred Foundation 19.
8. **Some historical roadmap text is now stale.** Earlier graph-foundation documents still describe later-implemented capabilities as â€œnot yet implemented.â€ Those statements are historical planning records, not current-state authority.
9. **Legacy-planner coexistence could create ambiguous planning authority.** Foundation 14 must eliminate silent fallback/dual-authority behavior in governed execution mode.
10. **Remote approvals create replay, identity, duplicate-command and secret-leak risks.** Foundation 16 makes these first-class acceptance requirements.
11. **Long-running real execution creates orphan/duplicate-run risk.** Foundation 16 requires durable run ownership/lease and replay-safe resume.
12. **Irreversible external actions cannot be treated like normal retryable code edits.** Foundation 14 requires explicit side-effect classification and pre-action authority.
13. **â€œExecutor-independent harnessâ€ could become an unsupported marketing claim.** Foundation 17 requires adapter-neutrality proof while avoiding unnecessary paid-provider expansion.
14. **Productization could continually contaminate foundation scope.** Section 5 explicitly separates commercial/enterprise/scale work from foundation completion.
15. **Canonical entity identity was not safe to assume.** False merge/duplication can distort convergence and repair scope. Foundation 13 makes identity/merge/split semantics a precondition for graph-governed repair.
16. **CONFLICTED needed mechanics, not a label.** Foundation 13 requires conflict sets and evidence-independence tracking.
17. **Weak graph paths could otherwise accumulate false authority.** Foundation 13 requires weakest-link epistemic composition.
18. **Operational store and graph can diverge.** Foundation 13 requires transactional/outbox consistency and fail-closed reconciliation for material split-brain.
19. **Retrieval misses could be misread as proof of absence.** Foundation 13/17 explicitly enforce and test `NO_MATCH != ABSENT`.
20. **Model-assisted graph assertions require reproducible provenance and independent challenge.** Foundation 13 binds reasoning provenance and verification.
21. **Graph complexity must earn its cost.** Foundation 17 adds a controlled graph-value gate and records latency/context/cost alongside quality.
22. **Convergence testing needs false-positive controls, not only planted positives.** Foundation 17 makes both error classes part of qualification.
23. **Retention/deletion, disaster recovery and migration controls are real production concerns but would improperly move the current foundation target.** They are explicitly post-foundation unless a concrete Foundation Complete blocker is proven.
24. **The broader V2 ongoing-management vision is product strategy, not a prerequisite for proving the execution-governance harness.** It is preserved as post-foundation productization rather than silently extending the foundation.

After assigning these gaps, no additional foundation stage is justified by the current authoritative requirements.

## 8. Current boundary

At the time this roadmap is frozen:

- Foundation 12 is the last accepted foundation;
- Foundation 13 is the next planned foundation;
- Foundation 13 is **not opened merely by this roadmap**;
- no Foundation 14â€“18 work is authorized by this roadmap;
- production remains untouched;
- neither application nor governance `main` is authorized for mutation by this roadmap.

The next implementation tranche begins only through explicit human authority.
