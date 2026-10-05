# GACM Trial â€” Current State

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

**GACM-GRAPH-FOUNDATION-13 — GRAPH-AWARE REPAIR PLANNING AND GRAPH INTEGRITY PRECONDITIONS — PASS**

Historical Phases 1â€“14 remain preserved as recorded below. GACM-MVP-CLOSURE-00 established the reconciled candidate authority at `0dd82e6176bd00e32fddfc975584a70773350b14`; Graph Foundation 01 established the graph kernel candidate at `150f895f4effa74dee116d51dd7fbee974445447`; Graph Foundation 03B established the graph-to-PilotHarness planning candidate at `25d67953c465abe91b2ad0f5e9378e24e78dcb45`; Graph Foundation 04 established durable graph persistence at `4ecc2ead93f185bb563b99ca87580c0d90a69e27`; Foundation 05 governance closed at `74b08065f138159f6e1d49841b7baf0e9e6fc534` and binds that exact engine to qualification-app candidate `19028a49b89a00be718ee017149a7615e966e4fd`.

On 2026-10-03 human authority instructed GACM to take the next action after Foundation 05 passed. Foundation 06 was therefore opened as the separately governed hosted-staging boundary and is now accepted. After that acceptance, human authority explicitly instructed GACM to continue to the end without tranche-by-tranche authorization and finish the MVP. Under the frozen MVP closure contract, that standing authority covers final audit, exact-candidate verification, qualification-app `main` promotion, post-promotion SETTLE, durable closure record, and final GACM closure-record promotion. Production mutation and post-MVP V2 expansion remain excluded.

## Phase history

- Phase 1 â€” Control-Layer Audit: **PASS** â€” commit `efc2622fdc46310c2aae7c12c6cb2e6291848aa4`
- Phase 2 â€” Durable Run-State Schema: **PASS** â€” commit `35f74bc84209591ccb19dec67fbeadb8e04779c2`
- Phase 3 â€” GitHub Authority Resolver: **PASS** â€” commit `cc9fb773aa31324a2f8e764e482de0516783ace5`
- Phase 4 â€” Graphify Discovery Adapter: **PASS** â€” commit `95f7d599c4ebc85fccfcbfce5522eeb14e17fd8f`
- Phase 5 â€” Authoritative Operational Context Resolver: **PASS** â€” commit `575315bab2cb5cc120af232a15597d36fb8ff4b7`
- Phase 6 â€” Deterministic Model Router: **PASS** â€” commit `cf53ee63fa6888b89cfbdff0e718405c26d7f5cb`
- Phase 7 â€” GCU Execution Adapter: **PASS** â€” commit `2277d3a`
- Phase 8 â€” Independent Verification Engine: **PASS** â€” commit `25d5c65`
- Phase 9 â€” Repair-Scope / Dependency Logic: **PASS** â€” commit `1998bea`
- Phase 10 â€” Placeholder and Identity Validator: **PASS** â€” commit `316e6e2f79dabb7a1a65a6acf569d32042b06e19`
- Phase 11 â€” Promotion / Rollback State Machine: **PASS** â€” commit `9c5fdc0eab0d22a4066a4f1d4cfb72b231901c53`
- Phase 12 â€” Post-Promotion Settle / Observation Gate: **PASS**
- Phase 13 â€” Pilot Harness: **PASS**
- Phase 14 â€” Real Project Pilot: **BLOCKED (historical)** â€” the former authoritative spec-skill baseline lacked the existing validators required by the selected work unit; that authority discrepancy is now resolved.
- Phase 14 â€” Real Project Pilot: **PASS** â€” exact SPEC candidate `30bfb0e78bab11c1e20cdc74b45530114c431654` was explicitly approved by Chris Kulbaba, promoted to SPEC `main`, independently verified, and SETTLED. Product repair cycles: 0; repair-process findings: 0.

## Current objective

Foundation 13 graph-aware repair planning and graph-integrity preconditions are accepted PASS on exact application candidate `df2ede96481f13905fe1dc9459a096cbebe329cc`, derived from accepted Foundation 12 application parent `f20cf367e8611025ffa1cb5e698db37350537c2c`. The exact candidate is preserved on remote branch `candidate/foundation13-graph-repair-planning-20261004`. Foundation 13 composes the accepted independent verifier and Phase 9 `RepairScopePlanner`, binds them to current graph/planning identity, preserves non-PASS verifier authority semantics, enforces graph identity/conflict/negative-retrieval controls, and emits only `CANDIDATE_REPAIR_PLANNING_ONLY` with `execution_authorized = false`. Targeted Foundation 08-13 regression 58/58 PASS, full application regression 202 tests plus 28 subtests PASS, compile/diff/secret/scope gates PASS, exact-SHA application CI run `37233740601` / job `111528636745` PASS, restart/reopen determinism PASS, and independent verification `verify-43b43a36f351086146238c5b` is authoritative PASS with `ARCHITECTURE_BEARING` scope and required broader requalification completed. Foundation 13 deliberately exposes no public repair-planning API; hosted staging/browser acceptance for the new internal component is `NOT_APPLICABLE`, while existing browser/runtime surfaces remain covered by the full regression. Both `main` branches and production remain untouched.

The reconciled authority set remains defined by `docs/GACM_MVP_AUTHORITY_MANIFEST_V1.md`. The graph-first operating contract is `docs/GACM_GRAPH_ENGINEERING_FOUNDATION_V1.md`; the Jev and graph-binding contract is `docs/GACM_JEV_CLASSIFICATION_AND_GRAPH_BINDING_V1.md`; the durable graph contract is `docs/GACM_GRAPH_DURABLE_PERSISTENCE_V1.md`; the application runtime contract is `docs/GACM_GRAPH_APPLICATION_RUNTIME_INTEGRATION_V1.md`; the Foundation 06 staging-authority contract is `docs/GACM_GRAPH_FOUNDATION_06_HOSTED_STAGING_AUTHORITY_V1.md`.

The authoritative SPEC `main` identity remains `30bfb0e78bab11c1e20cdc74b45530114c431654`. The authoritative CRIT `main` identity remains `187b7f7d3d63025f98386da09255942d6693303d`. Foundation 05 and Foundation 06 identities remain preserved as historical parents/evidence; the exact final MVP application candidate is now `32d474fdb8fe0672d826ff434b4bfc94c9537407`.

Foundation 13 graph-aware repair planning and graph-integrity preconditions are now the accepted current boundary. Foundation 14 — Governed Candidate-Tranche Execution Bridge — is the next frozen-roadmap capability, but it is not opened by this record. Authoritative causal claims, automatic repair execution, automatic repair approval, scope expansion, provider/model/tool selection, production mutation, and either `main` merge remain excluded.

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

**STOP at the accepted Foundation 13 boundary.** Foundation 14 - Governed Candidate-Tranche Execution Bridge - is the next frozen-roadmap stage but is not opened by this acceptance. Production mutation and either `main` merge remain excluded.

Current execution state: `PASS - FOUNDATION_13_ACCEPTED_STOP_BOUNDARY`.

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


## Permanent governance correction â€” generalization

On 2026-09-20, human authority explicitly authorized a governance-system correction establishing `GACM-GENERALIZATION-AND-WHOLE-SYSTEM-GATE`. This authorization is additive to the historical phase record and supersedes the prior methodology freeze only for this control correction.

Future governed product-repair runs must freeze a product-level definition of done and connected-system map before execution, preserve that acceptance boundary, require independent generalized evidence before promotion, separate fresh-input generalization from reference regression, scan for fixture dependencies, and fail closed on missing generalization proof.

Permanent escape classes: `FIXTURE_TARGET_COLLAPSE` and `SEQUENTIAL_BLOCKER_TUNNELING`.

The machine enforcement implementation lives in `src/gacm/generalization/`, the Pilot Harness pre-execution and pre-promotion gates, PromotionEligibility, and the durable run-state schema release 1.1.0 controls.

## Permanent governance correction â€” external provider authority

On 2026-09-30, human authority explicitly authorized an additive universal governance correction establishing `GACM-EXTERNAL-PROVIDER-AUTHORITY-AND-CREDENTIAL-PROVENANCE-GATE`.

Permanent failure patterns:

- `EXTERNAL_PROVIDER_AUTHORITY_UNDER_SPECIFICATION`
- `CREDENTIAL_PROVENANCE_UNDER_SPECIFICATION`

Future governed authenticated external actions must prove provider/service authority and credential provenance before network execution. Ambient/global credentials and provider discovery are diagnostic only and may not become configuration automatically. Provider substitution is HOLD unless explicitly authorized. Paid-call authorization does not select or authorize a provider.

The gate must execute before parity/currentness so a self-consistent but unauthorized provider configuration cannot pass by internal consistency alone.

Durable handoff/restart state must preserve the non-secret governed provider identity and authority reference.

## Permanent governance correction - execution authority and inference state

On 2026-10-04, human authority explicitly authorized an additive GACM-wide correction establishing the mandatory `GACM Execution Authority and Inference State Contract v1` and permanent control `CL-43`.

Core invariant: unbounded inference is permitted during design. Once a work-unit execution recipe is frozen, unbounded inference is revoked. During execution, the executor may act only through machine-authorized actions and explicitly declared bounded-judgment slots.

Canonical execution-authority states are `DESIGN -> FROZEN -> EXECUTION -> VERIFICATION`; any authority, recipe, identity, transition or action mismatch produces `BLOCKED`.

Every future execution-ready work unit must bind a versioned `GACM_EXECUTION_RECIPE_V1` to work-unit/package/run-state identity. The GCU execution boundary must issue deterministic `ALLOW` or `DENY` before each material action based on the current frozen step, tool/action type, target, parameters, acceptable prior state, bounded judgment and expected evidence-bearing result transition.

Availability never creates authority. An installed tool, command, credential, provider, model, dependency, environment variable or workaround is not executable merely because it exists.

The executor may not edit its own recipe. Invalid or unexpected runtime state stops execution; any revised approach requires leaving EXECUTION, governed diagnosis, explicit re-authorization, a new frozen recipe digest/package identity, and only then resumed execution.

The machine enforcement implementation lives in `src/gacm/execution/action_authority.py`, the GCU execution adapter, graph scheduler/binder, execution policy, durable run-state schema and associated negative-path tests. This correction is cross-cutting and precedes Foundation 10; it does not redefine Foundation 10 or reopen the closed MVP.

Acceptance identity: implementation candidate `8ae0eb6779972d5da0c326e6820f6704aa209877`; independent verification `verify-4ea554fa7257310fe0a81c03` authoritative PASS; scope classification `AUTHORITY_BEARING`; targeted 85/85 PASS; full governance regression 258/258 PASS; exact-SHA CI PASS.

## Foundation 10 authority

Foundation 10 opened on 2026-10-04 from governance parent `4bd875e268fa2700e5aa945711ebe65213adc587`. The governing contract is `docs/GACM_GRAPH_FOUNDATION_10_RELEASE_ACCEPTANCE_V1.md`. The accepted qualification-app staging candidate under live proof remains `85944f28dfbc3eeffce152a2ee022d52a0b4f41c`; this tranche does not authorize promoting it. CL-43 remains mandatory for every execution-ready work unit.

Foundation 10 acceptance identity: governance implementation `5dcaa68227169e0db7c857251748205ac7e1e5d1`; independent verification `verify-2404d6cc5f582031022df0f8` authoritative PASS; live graph-release evidence digest `ff06d747878542687aa9f39fb9c5c883751b4d44806b9c1a4fd6911f28fc21a5`; targeted 60/60 PASS; full governance regression 274/274 PASS; exact implementation CI PASS; application/Railway/production unchanged.

## Foundation 11 authority

Foundation 11 opened on 2026-10-04 from accepted Foundation 10 governance SHA `e93a1f2b50feff47490dde4e99236d2a2f55b209` and accepted Foundation 09 application SHA `85944f28dfbc3eeffce152a2ee022d52a0b4f41c`. The governing contract is `docs/GACM_GRAPH_FOUNDATION_11_FAILURE_PATTERN_RETRIEVAL_V1.md`. The authoritative initial registry is `docs/GACM_FAILURE_PATTERN_REGISTRY_V1.json`. Only patterns already explicitly governed as `GENERALIZED` may be exposed across project boundaries; no new generalization authority is created by this tranche. CL-43 remains mandatory.

Foundation 11 acceptance identity: app candidate `0f8d226b8bb28c90abf57ce5ba4f275df0d875c3`; Railway staging deployment `daa1b9bf-0d42-4ccf-90a2-5a6e4e16b844`; registry SHA-256 `9e0d22671581fa2086e78505e5f7032e3d28309591ac7cbe1713e1b54dea599d`; independent verification `verify-a7f2c324ad6545e8a63e6a9b` authoritative PASS; targeted 44/44 PASS; full app regression 174/174 PASS; exact-SHA app CI, live API, Edge browser, restart/reopen and currentness PASS.

## Foundation 12 authority

Foundation 12 opened on 2026-10-04 from accepted Foundation 11 governance SHA `0e0195265dd04cbbc2c4a8572663e824e3639c35` and accepted Foundation 11 application SHA `0f8d226b8bb28c90abf57ce5ba4f275df0d875c3`. Governing contract: `docs/GACM_GRAPH_FOUNDATION_12_PRD_TRANCHE_GENERATION_V1.md`. Existing human PRD semantics are frozen; graph output may govern candidate planning/currentness but cannot create product truth or execution authority.

Foundation 12 acceptance identity: application candidate `f20cf367e8611025ffa1cb5e698db37350537c2c`; Railway staging deployment `4f84c4a9-e3f7-4e39-a41f-1f9adc5b2ed4`; independent verification `verify-7b8c71d8a5775bd9195a55c0` authoritative PASS; targeted planning 9/9 PASS; graph/retrieval/convergence regression 62/62 PASS; full application regression 183/183 PASS; exact-SHA app CI, live API/currentness, real Edge browser and restart/reopen identity PASS. No production mutation or `main` merge occurred.

## Foundation completion roadmap authority

On 2026-10-04, human authority explicitly instructed GACM to freeze and audit the remaining Foundation roadmap so the completion target cannot continue moving.

The frozen roadmap is `docs/GACM_FOUNDATION_COMPLETION_ROADMAP_V1.md`.

The accepted Foundation 13 boundary is current. The fixed remaining sequence is Foundation 14 through Foundation 18, with Foundation 18 defined as capability-free whole-foundation closure. There is no implied Foundation 19.

Foundation 13 was explicitly opened after the roadmap freeze and is now accepted PASS. Foundation 14 — Governed Candidate-Tranche Execution Bridge — is the next planned capability and remains not opened by this record. A later capability may enter or alter the frozen Foundation sequence only through an explicit human-authorized roadmap amendment proving that the change is required to satisfy the frozen Foundation Complete definition.

Production mutation and either `main` merge remain outside this roadmap authority.

## Foundation 13 authority

On 2026-10-04, human authority explicitly opened Graph Foundation 13 from the frozen completion roadmap.

Foundation 13 governing contract: docs/GACM_GRAPH_FOUNDATION_13_REPAIR_PLANNING_V1.md.

Foundation 13 objective is graph-aware repair planning plus the graph-integrity preconditions required before graph-derived reasoning can influence repair scope. Output authority is CANDIDATE_REPAIR_PLANNING_ONLY; repair execution, execution-recipe creation, automatic approval, scope expansion, provider/model/tool selection, production mutation, either main merge, and Foundation 14 remain excluded.

Governance parent is 6df6e99e3cf896862f220d9f1320866a569a87ea. Application parent is f20cf367e8611025ffa1cb5e698db37350537c2c.

Foundation 13 acceptance identity: application candidate `df2ede96481f13905fe1dc9459a096cbebe329cc`; application parent `f20cf367e8611025ffa1cb5e698db37350537c2c`; exact-SHA application CI run `37233740601` / job `111528636745` PASS; targeted regression 58/58 PASS; full application regression 202 tests plus 28 subtests PASS; independent verification `verify-43b43a36f351086146238c5b` authoritative PASS; scope `ARCHITECTURE_BEARING`; broader requalification required and completed. Hosted staging/browser proof for the Foundation 13 internal-only component is `NOT_APPLICABLE`; no public repair-planning endpoint exists. Production and both `main` branches remain untouched.

Current execution state: `PASS - FOUNDATION_13_ACCEPTED_STOP_BOUNDARY`.


### Foundation 13 contract correction — verifier/repair authority

Implementation diagnosis found a semantic contradiction in the initial Foundation 13 freeze: the existing `VerificationReceipt` contract permits `authoritative = true` only for an independent verifier `PASS`, so a repair-triggering `FAIL/BLOCKED/UNOBSERVABLE` receipt cannot truthfully be marked authoritative.

The Foundation 13 contract is corrected without expanding scope: non-PASS receipts must preserve the existing independent-verifier semantics; the accepted Phase 9 `RepairScopePlanner` remains the repair-scope authority rather than being reimplemented; and Foundation 13 remains an internal component boundary with no untrusted public repair-planning endpoint before Foundation 14 supplies trusted execution/verification binding.
