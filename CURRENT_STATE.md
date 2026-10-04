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

GACM v4.2.2 remains the frozen base methodology authority. Explicitly authorized additive governance corrections and V2 architecture specifications are also recorded in this repository. The MVP closure contract excluded V2 graph runtime work by default; on 2026-10-03 explicit human authority authorized bounded Graph Foundation 01, Graph Foundation 02, the Foundation 03A live Jev smoke, Graph Foundation 03B planning integration, Graph Foundation 04 durable persistence/reconstruction, Graph Foundation 05 application/runtime browser integration, and then the Foundation 06 hosted-staging boundary. Full V2 runtime expansion remains separately governed.

## Current phase

**GACM-GRAPH-FOUNDATION-07 — GRAPH-AWARE CRIT — PASS**

Historical Phases 1–14 remain preserved as recorded below. GACM-MVP-CLOSURE-00 established the reconciled candidate authority at `0dd82e6176bd00e32fddfc975584a70773350b14`; Graph Foundation 01 established the graph kernel candidate at `150f895f4effa74dee116d51dd7fbee974445447`; Graph Foundation 03B established the graph-to-PilotHarness planning candidate at `25d67953c465abe91b2ad0f5e9378e24e78dcb45`; Graph Foundation 04 established durable graph persistence at `4ecc2ead93f185bb563b99ca87580c0d90a69e27`; Foundation 05 governance closed at `74b08065f138159f6e1d49841b7baf0e9e6fc534` and binds that exact engine to qualification-app candidate `19028a49b89a00be718ee017149a7615e966e4fd`.

On 2026-10-03 human authority instructed GACM to take the next action after Foundation 05 passed. Foundation 06 was therefore opened as the separately governed hosted-staging boundary and is now accepted. After that acceptance, human authority explicitly instructed GACM to continue to the end without tranche-by-tranche authorization and finish the MVP. Under the frozen MVP closure contract, that standing authority covers final audit, exact-candidate verification, qualification-app `main` promotion, post-promotion SETTLE, durable closure record, and final GACM closure-record promotion. Production mutation and post-MVP V2 expansion remain excluded.

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

Foundation 07 graph-aware CRIT is accepted PASS on exact application candidate `0ff481f0a6a84146fe3ac1c7fd759adb7e5b8e24`, preserved on remote candidate branch and deployed only to isolated Railway staging as `65dbc434-cdcb-461d-8805-80612bce29d4`. Qualification-app `main` remains the closed MVP authority `32d474fdb8fe0672d826ff434b4bfc94c9537407`; GACM `main` remains `c50ba6e5f5382b3460f0ab1de7d508f330ced800` until this Foundation 07 governance acceptance record is separately promoted in a future governed release decision. Graph context is bounded and advisory-only, exact question/answer graph provenance is durable, stale/malformed context fails closed, 90/90 targeted tests PASS, 8/8 graph-aware/fresh-input tests PASS, 144/144 full regression PASS, exact-SHA app CI PASS, live OpenAI `gpt-6-luna` provenance/currentness PASS, real Edge acceptance PASS, and independent verification `verify-d7575320fe6573daa44cbe7f` is authoritative PASS. The delta is correctly MODEL_BEARING and its required broader requalification is complete. Production remains untouched.

The reconciled authority set remains defined by `docs/GACM_MVP_AUTHORITY_MANIFEST_V1.md`. The graph-first operating contract is `docs/GACM_GRAPH_ENGINEERING_FOUNDATION_V1.md`; the Jev and graph-binding contract is `docs/GACM_JEV_CLASSIFICATION_AND_GRAPH_BINDING_V1.md`; the durable graph contract is `docs/GACM_GRAPH_DURABLE_PERSISTENCE_V1.md`; the application runtime contract is `docs/GACM_GRAPH_APPLICATION_RUNTIME_INTEGRATION_V1.md`; the Foundation 06 staging-authority contract is `docs/GACM_GRAPH_FOUNDATION_06_HOSTED_STAGING_AUTHORITY_V1.md`.

The authoritative SPEC `main` identity remains `30bfb0e78bab11c1e20cdc74b45530114c431654`. The authoritative CRIT `main` identity remains `187b7f7d3d63025f98386da09255942d6693303d`. Foundation 05 and Foundation 06 identities remain preserved as historical parents/evidence; the exact final MVP application candidate is now `32d474fdb8fe0672d826ff434b4bfc94c9537407`.

Graph-aware CRIT is now accepted at the Foundation 07 boundary. Bounded retrieval is the next roadmap item, but no retrieval tranche is opened by this record. Embeddings, convergence/shared-root detection, legacy-planner removal, cross-project learning, graph-triggered execution, provider/model changes, and production migration remain excluded.

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

STOP at the Foundation 07 boundary. The accepted application candidate remains isolated in staging and is not promoted to qualification-app `main` by this tranche. Bounded retrieval is the next roadmap item only after a separate governed objective is opened.

Current execution state: `PASS — FOUNDATION_07_GRAPH_AWARE_CRIT_ACCEPTED / STOP AT TRANCHE BOUNDARY`.

### Historical / deferred items

- qualification-app Foundation 05 candidate `19028a49b89a00be718ee017149a7615e966e4fd` is remotely preserved and exact-SHA CI/browser accepted but is not merged to app `main`;
- GACM `main` remains unprotected;
- the pre-reconciliation current-state record was stale relative to later governance/V2 work;
- Codex CLI `gpt-5.6-luna` was invoked read-only during the preceding reconciliation tranche but its internal command helper failed before repository access with `helper_unknown_error: setup refresh had errors`; no model escalation or additional model session was used;
- the legacy automatic Terra/Sol routing defect is resolved in this candidate: Luna is the only automatic route, while non-Luna selection/escalation requires explicit durable human model authority;
- graph-derived work packages remain bound to GCU contracts; Foundation 04 durable persistence is wired into the actual qualification application runtime through Foundation 05; Foundation 06 Railway staging authority is explicit; first deployment `0ab21434-8a7c-44c1-a024-601d948bc089` at app SHA `19028a49...` reached provider SUCCESS but acceptance remains HOLD; the bounded identity-repair candidate `7341b9c89869528eeafc2704984dbe9115d2dabc` passed 34/34 targeted, 128/128 full regression and exact-SHA app CI and is authorized for redeploy;
- PilotHarness remains the accepted lifecycle owner; Graph Foundation 03B adds an explicit graph-authoritative planning mode while preserving the legacy planner as the default/shadow path until graph scheduling is independently accepted;
- TypeSafe Jev remains an advisory classifier boundary; Foundation 03A proved one live authenticated governed `POST /v1/systemone` path, with `jev-latest` resolving to `jev-1.13.0`, projection only as `INFERRED`, and GraphScheduler returning `COLLECT_EVIDENCE`; Jev is not graph truth;
- `jev-latest` is a provider alias, so the runtime records requested/resolved model and request/result digests; immutable provider-version currentness remains a future hardening item if TypeSafe exposes a durable version identity;
- Foundation 06 final deployment `533ddf19-a148-49dd-8574-30a75e5e15e1` / app SHA `d8452cdf040d75360e711c994c2b911189d4842c` remains preserved as the accepted parent. Final MVP closure supersedes it only by adding the deterministic acceptance entrypoint/generalization closure proof on app SHA `32d474fdb8fe0672d826ff434b4bfc94c9537407`, deployed as `3753fec4-9746-4bef-aa07-7c433d8704f6`; all pre-promotion closure gates PASS and production remains untouched;
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
