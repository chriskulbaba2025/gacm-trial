# GACM Trial — Current State

## Authoritative repository

`chriskulbaba2025/gacm-trial`

## Repository identity

The checked-out repository `HEAD` is the authoritative repository commit identity.

The exact SHA must be obtained from Git at execution time. This file defines governed project state and does not duplicate the SHA of the commit that contains it.

Before governed work begins, execution must verify the local `HEAD` against the intended remote and/or explicitly authorized `HEAD` identity.

## Authoritative implementation PRD

`GACM_IMPLEMENTATION_PRD_V1.0.md`

## Methodology status

GACM v4.2.2 remains the frozen base methodology authority. Explicitly authorized additive governance corrections and V2 architecture specifications are also recorded in this repository. The MVP closure contract excluded V2 graph runtime work by default; on 2026-10-03 explicit human authority authorized bounded Graph Foundation 01 and then Graph Foundation 02. Full V2 runtime expansion remains separately governed.

## Current phase

**GACM-GRAPH-FOUNDATION-02 — JEV CLASSIFICATION + ROUTING AUTHORITY + GRAPH EXECUTION BINDING**

Historical Phases 1–14 remain preserved as recorded below. GACM-MVP-CLOSURE-00 established the reconciled candidate authority at `0dd82e6176bd00e32fddfc975584a70773350b14`; Graph Foundation 01 established the graph kernel candidate at `150f895f4effa74dee116d51dd7fbee974445447`.

On 2026-10-03 human authority explicitly authorized the next bounded graph tranche. This tranche adds a TypeSafe Jev advisory classification layer, reconciles model routing to Luna-first with explicit durable human authority for any non-Luna model, and binds graph action/revision identity into durable run-state and GCU execution contracts. It does not authorize merge, deployment, production mutation, autonomous model escalation, subagents, graph retrieval, Neo4j/pgvector, convergence, PilotHarness lifecycle replacement, or full V2 migration.

## Phase history

- Phase 1 — Control-Layer Audit: **PASS** — commit `efc2622fdc46310c2aae7c12c6cb2e6291848aa4`
- Phase 2 — Durable Run-State Schema: **PASS** — commit `35f74bc84209591ccb19dec67fbeadb8e04779c2`
- Phase 3 — GitHub Authority Resolver: **PASS** — commit `cc9fb773aa31324a2f8e764e482de0516783ace5`
- Phase 4 — Graphify Discovery Adapter: **PASS** — commit `95f7d599c4ebc85fccfcbfce5522eeb14e17fd8f`
- Phase 5 — Authoritative Operational Context Resolver: **PASS** — commit `575315bab2cb5cc120af232a15597d36fb8ff4b7`
- Phase 6 — Deterministic Model Router: **PASS** — commit `cf53ee63fa6888b89cfbdff0e718405c26d7f5cb`
- Phase 7 — GCU Execution Adapter: **PASS** — commit `2277d3a`
- Phase 8 — Independent Verification Engine: **PASS** — commit `25d5c65`
- Phase 9 — Repair-Scope / Dependency Logic: **PASS** — commit `1998bea`
- Phase 10 — Placeholder and Identity Validator: **PASS** — commit `316e6e2f79dabb7a1a65a6acf569d32042b06e19`
- Phase 11 — Promotion / Rollback State Machine: **PASS** — commit `9c5fdc0eab0d22a4066a4f1d4cfb72b231901c53`
- Phase 12 — Post-Promotion Settle / Observation Gate: **PASS**
- Phase 13 — Pilot Harness: **PASS**
- Phase 14 — Real Project Pilot: **BLOCKED (historical)** — the former authoritative spec-skill baseline lacked the existing validators required by the selected work unit; that authority discrepancy is now resolved.
- Phase 14 — Real Project Pilot: **PASS** — exact SPEC candidate `30bfb0e78bab11c1e20cdc74b45530114c431654` was explicitly approved by Chris Kulbaba, promoted to SPEC `main`, independently verified, and SETTLED. Product repair cycles: 0; repair-process findings: 0.

## Current objective

Prove the first usable graph-first execution handoff: cheap advisory semantic classification can create non-authoritative graph candidates; deterministic graph state decides what evidence is needed; routing cannot silently upgrade models; and only an exact graph-bound machine contract can reach the GCU execution gate.

The reconciled authority set remains defined by `docs/GACM_MVP_AUTHORITY_MANIFEST_V1.md`. The graph-first operating contract is `docs/GACM_GRAPH_ENGINEERING_FOUNDATION_V1.md`; the Jev and graph-binding contract is `docs/GACM_JEV_CLASSIFICATION_AND_GRAPH_BINDING_V1.md`.

The authoritative SPEC `main` identity remains `30bfb0e78bab11c1e20cdc74b45530114c431654`. The authoritative CRIT `main` identity remains `187b7f7d3d63025f98386da09255942d6693303d`. The recovered Human CRIT MVP candidate remains `132cff6d3280e3fe8f86b23a0113cab986df03e3`.

Full V2 graph persistence, retrieval, graph-aware CRIT, convergence, PilotHarness scheduler replacement, and production migration remain outside this tranche.

## Completed phases

The Phase 1 control-layer audit, Phase 2 durable run-state schema, Phase 3 GitHub Authority Resolver, Phase 4 Graphify Discovery Adapter, Phase 5 Authoritative Operational Context Resolver, Phase 6 Deterministic Model Router, Phase 7 GCU Execution Adapter, Phase 8 Independent Verification Engine, Phase 9 Repair-Scope / Dependency Logic, Phase 10 Placeholder and Identity Validator, Phase 11 Promotion / Rollback State Machine, Phase 12 SETTLE gate, and Phase 13 Pilot Harness are complete. Their artifacts and completion proofs remain the evidence for the recorded PASS states.

## Historical Phase 1 requirements

The Phase 1 audit was required to cover every control:

1. Control ID
2. Control statement
3. Failure prevented
4. Current/assumed enforcement layer
5. Correct enforcement layer
6. Whether the model can bypass it
7. Whether stale memory can bypass it
8. Whether ambiguity can bypass it
9. Required machine enforcement
10. Required evidence/proof
11. Dependencies on other controls
12. Implementation priority

The audit explicitly covered:

- GitHub authority
- Graphify discovery only, never authority
- authoritative operational context resolution
- account / tenant / environment / region / repository identity
- placeholder prevention
- model routing
- GCU execution boundaries
- independent verification
- bounded repair
- affected-scope re-verification
- broader requalification triggers
- durable run state
- rollback
- SETTLE
- human authority
- continuation across chats/sessions without chat memory

## Historical Phase 1 stop condition

No code, Graphify integration, model routing, or orchestration was to be implemented during Phase 1. Any contradiction preventing deterministic control placement was to be documented and stopped rather than resolved by silently choosing a design.

## Phase 12 gate

Phase 12 requires Phase 11 `SETTLE_REQUIRED`, exact promoted identity, preserved prior authority, valid rollback target, and unchanged authority continuity. It is complete and does not authorize Phase 13.

Preserve repository HEAD as the runtime-authoritative repository identity, GitHub as durable authority, Graphify as discovery only, and frozen GACM v4.2.2 methodology.

## Phase 13 gate

Phase 13 is orchestration integration only. The Pilot Harness coordinates existing controls, preserves durable evidence, supports resume and bounded repair, respects human promotion authority, and does not start a real project or integrate Hermes.

## Phase 14 promotion and settlement

The promoted SPEC identity is `30bfb0e78bab11c1e20cdc74b45530114c431654` on local and remote `main`. The candidate changed only `scripts/spec_readiness.py` and `tests/test_spec_readiness.py`; authoritative validators and forbidden surfaces were preserved. Explicit human approval, independent verification, promotion, and SETTLE receipts are recorded in the durable Phase 14 run state. Rollback target remains `1264a0d4bf0bf4423f116126039bf695671aa91e`; rollback did not occur.

## Next authorized action

Complete `GACM-GRAPH-FOUNDATION-02` only:

1. preserve Jev as advisory classification, never authority;
2. require inferred/hypothesis classifier output to collect stronger evidence before governing work;
3. keep Luna as the only automatic execution-model route;
4. require explicit durable human authority for any non-Luna route or escalation;
5. bind exact graph action/revision/target/project identity into run state and GCU execution contracts;
6. prove stale/mismatched graph state, route identity, subagent authorization, and external-action classification fail closed;
7. run targeted tests and the complete GACM regression;
8. push the exact candidate branch and verify candidate CI;
9. STOP before PilotHarness scheduler replacement, merge, deployment, or promotion.

Any next graph tranche requires explicit authorization.

### Current HOLD items

- qualification-app candidate `132cff6d...` is recovered and remotely preserved but is not promoted to app `main`;
- GACM `main` remains unprotected;
- the pre-reconciliation current-state record was stale relative to later governance/V2 work;
- Codex CLI `gpt-5.6-luna` was invoked read-only during the preceding reconciliation tranche but its internal command helper failed before repository access with `helper_unknown_error: setup refresh had errors`; no model escalation or additional model session was used;
- the legacy automatic Terra/Sol routing defect is resolved in this candidate: Luna is the only automatic route, while non-Luna selection/escalation requires explicit durable human model authority;
- graph-derived work packages are now bound to GCU contracts, but the in-process graph is not yet durably persisted/reconstructed across process restart;
- the existing PilotHarness still owns procedural lifecycle/planning and has not yet been replaced by GraphScheduler output;
- TypeSafe Jev is integrated as an advisory classifier boundary; live authenticated inference remains an external action subject to provider/credential authority and is not treated as graph truth;
- `jev-latest` is a provider alias, so the runtime records requested/resolved model and request/result digests; immutable provider-version currentness remains a future hardening item if TypeSafe exposes a durable version identity;
- production remains untouched.


## Permanent governance correction — generalization

On 2026-09-20, human authority explicitly authorized a governance-system correction establishing `GACM-GENERALIZATION-AND-WHOLE-SYSTEM-GATE`. This authorization is additive to the historical phase record and supersedes the prior methodology freeze only for this control correction.

Future governed product-repair runs must freeze a product-level definition of done and connected-system map before execution, preserve that acceptance boundary, require independent generalized evidence before promotion, separate fresh-input generalization from reference regression, scan for fixture dependencies, and fail closed on missing generalization proof.

Permanent escape classes: `FIXTURE_TARGET_COLLAPSE` and `SEQUENTIAL_BLOCKER_TUNNELING`.

The machine enforcement implementation lives in `src/gacm/generalization/`, the Pilot Harness pre-execution and pre-promotion gates, PromotionEligibility, and the durable run-state schema release 1.1.0 controls.

## Permanent governance correction — external provider authority

On 2026-09-30, human authority explicitly authorized an additive universal governance correction establishing `GACM-EXTERNAL-PROVIDER-AUTHORITY-AND-CREDENTIAL-PROVENANCE-GATE`.

Permanent failure patterns:

- `EXTERNAL_PROVIDER_AUTHORITY_UNDER_SPECIFICATION`
- `CREDENTIAL_PROVENANCE_UNDER_SPECIFICATION`

Future governed authenticated external actions must prove provider/service authority and credential provenance before network execution. Ambient/global credentials and provider discovery are diagnostic only and may not become configuration automatically. Provider substitution is HOLD unless explicitly authorized. Paid-call authorization does not select or authorize a provider.

The gate must execute before parity/currentness so a self-consistent but unauthorized provider configuration cannot pass by internal consistency alone.

Durable handoff/restart state must preserve the non-secret governed provider identity and authority reference.
