# GACM Pilot v1 — Control-Layer Audit

**Phase:** 1 — Control-Layer Audit
**Audit date:** 2026-09-14
**Repository:** `chriskulbaba2025/gacm-trial`
**Authorized starting SHA:** `d5d80587cdac0a1d104899f234206c2c35ba28d9`
**Audited candidate:** `d5d80587cdac0a1d104899f234206c2c35ba28d9` at audit start
**Model:** GPT-5.6 Sol / High
**Scope:** architecture/control placement only; no application implementation, Graphify installation, Hermes integration, or continual learning.

## Executive determination

The PRD has a coherent control-plane direction and names the required boundaries, but it does not yet have deterministic implementation. The lowest-layer placement is generally unambiguous when “ownership” is separated from “evidence” and “human authorization” is separated from machine enforcement. The decisive design is:

```text
GitHub durable authority → GACM orchestration/state/policy → GCU bounded execution
                                  ↓
                     independent verification → release/SETTLE
```

Graphify is discovery/index only. The model may reason and propose within a frozen work unit; it cannot resolve authoritative identity, grant permissions, classify repair breadth by itself, certify PASS, promote, settle, or rewrite policy.

The audit is complete as a control-placement artifact, but the Phase 1 gate is **BLOCKED** for implementation/release purposes pending resolution of the repository identity discrepancy recorded below and implementation of the deterministic controls marked `MISSING` or `PREREQUISITE`. This is a control-layer audit result, not a claim that Pilot v1 is ready.

### Repository truth discrepancy — BLOCKER B-01

`CURRENT_STATE.md` identifies `f059819e0384f3fa1591e1e3ba7784534372d9d4` as the current authoritative commit, while the user-authorized starting SHA and actual `HEAD`/`origin/main` are `d5d80587cdac0a1d104899f234206c2c35ba28d9`. The latter is the parent-plus-governance commit containing `CURRENT_STATE.md`; the documents do not agree on the authoritative identity. Phase 2 must not begin until a human-authorized correction or explicit superseding identity record resolves this. No governing file was changed in this run.

## Audit method and status vocabulary

“Current enforcement” means what the present repository can enforce, not what the PRD intends. Since the repository contains only the two governing documents, all runtime controls are currently `UNIMPLEMENTED`. “Correct layer” is the lowest allowed layer capable of deterministic prevention. A higher layer may supply evidence, approval, or a narrower gate, but it does not displace the owning layer.

Statuses used in the matrix:

- `MISSING` — no deterministic implementation exists in the audited repository.
- `PREREQUISITE` — required design contract for a later implementation; not a PASS.
- `PASS-PLACEMENT` — ownership is deterministically assigned by this audit; implementation proof remains required.
- `BLOCKED` — placement or progression is blocked by unresolved authority/identity evidence.

## Complete control matrix

Each row includes the twelve required audit dimensions: ID, statement, prevented failure, current/assumed layer, correct layer, ownership rationale, model bypass, stale-memory bypass, ambiguity bypass, machine enforcement, proof, dependencies, and priority. `M` = model can bypass; `S` = stale memory can bypass; `A` = ambiguous context can bypass.

| ID | Control statement; failure prevented | Current / assumed → correct layer; why owner | Bypass risk (M/S/A) | Required deterministic machine enforcement | Required proof / evidence | Dependencies | Priority |
|---|---|---|---|---|---|---|---|
| CL-01 | GitHub and approved version-controlled durable state remain authority; prevents chat/model/harness memory becoming canonical. | Prompt/documentation → DURABLE AUTHORITY; authority must be read from immutable durable state. | M/S/A: YES | Pin source, ref, commit, content digest, read-only/authorized write mode; reject unapproved authority stores. | Resolution receipt with source/ref/SHA/digest and negative test against chat-only value. | CL-02, CL-03, CL-23 | P0 |
| CL-02 | Graphify discovers relationships and sources but never authorizes facts; prevents indexed/stale/wrong-project data becoming authority. | DISCOVERY / GRAPH → DISCOVERY / GRAPH plus DURABLE AUTHORITY gate; Graphify owns discovery only. | M/S/A: YES | Attach provenance to each discovery result; require authoritative source resolution before use; no Graphify write path to policy/state. | Discovery-to-authority trace for every material fact; rejection test for graph-only fact. | CL-01, CL-03 | P0 |
| CL-03 | Every material Graphify fact resolves back to an authoritative durable source before execution; prevents graph hallucination/staleness. | Model instruction → ORCHESTRATION + DURABLE AUTHORITY; orchestration owns the pre-execution join. | M/S/A: YES | Require source URI/ref/SHA and value equality; fail closed on missing, conflicting, or unverifiable provenance. | Per-field resolution record and conflict/absence tests. | CL-01, CL-02, CL-04 | P0 |
| CL-04 | Resolve exactly one authoritative operational context before sensitive work; prevents guess/selection drift. | Model/harness retrieval → ORCHESTRATION; it can stop execution before inference/action. | M/S/A: YES | Context resolver returns one immutable context or `AUTHORITY_AMBIGUOUS`; no model choice of candidate. | Context receipt: candidate set, selected source, proof, resolver version, outcome. | CL-01, CL-03, CL-05–CL-17 | P0 |
| CL-05 | Account identity is authoritative and bound to the run; prevents wrong-account action or substituted account. | Prompt → DURABLE AUTHORITY + ORCHESTRATION; identity is an input contract, not a suggestion. | M/S/A: YES | Require canonical account ID, source, and equality checks at entry, service, persistence, reload, job, provider, and terminal output. | Negative cross-account test and identity continuity chain. | CL-04, CL-23, CL-33 | P0 |
| CL-06 | Tenant identity is authoritative and isolated; prevents cross-tenant reads/writes. | Prompt/auth middleware → DURABLE AUTHORITY + ORCHESTRATION; authorization boundary owns tenancy. | M/S/A: YES | Derive tenant from authenticated authority; scope every query/job/artifact; reject client-supplied substitution. | Cross-tenant denial test, persisted tenant trace, reload/recovery proof. | CL-04, CL-05, CL-23 | P0 |
| CL-07 | Client/project identity is authoritative; prevents work applied to a similarly named project. | Prompt → DURABLE AUTHORITY + ORCHESTRATION; project binding controls scope. | M/S/A: YES | Immutable project ID plus repository/branch/worktree binding; exact equality at all handoffs. | Project identity receipt and wrong-project rejection test. | CL-01, CL-04, CL-08 | P0 |
| CL-08 | Repository identity is exact; prevents execution against wrong repository/fork. | Prompt/working directory → DURABLE AUTHORITY + EXECUTION / GCU; authority resolves, GCU verifies target. | M/S/A: YES | Canonical remote identity, repository ID, worktree path, and candidate SHA must match before tools run. | Preflight log plus remote/SHA mismatch test. | CL-01, CL-07, CL-21 | P0 |
| CL-09 | Branch identity is explicit; prevents writes to stable/protected branch. | Model convention → DURABLE AUTHORITY + EXECUTION / GCU; write boundary can reject target. | M/S/A: YES | Require exact branch/ref and protected-branch policy; reject detached/unknown target unless explicitly governed. | Branch/worktree receipt and protected-target denial. | CL-08, CL-21, CL-31 | P0 |
| CL-10 | Environment identity is explicit; prevents staging/production confusion. | Prompt/config → DURABLE AUTHORITY + ORCHESTRATION; environment is part of context. | M/S/A: YES | Enumerated environment ID, immutable target mapping, and environment-specific allowlist; no inferred default. | Environment mapping proof and wrong-environment negative test. | CL-04, CL-11, CL-18 | P0 |
| CL-11 | Cloud account and region are authoritative; prevents wrong cloud account/region and data locality errors. | Prompt/env vars → DURABLE AUTHORITY + EXECUTION / GCU preflight; target identity must be checked before side effects. | M/S/A: YES | Require canonical account/region pair; validate provider session and target before credential use/action. | Provider identity receipt, region mismatch test, no-default test. | CL-05, CL-10, CL-16 | P0 |
| CL-12 | Deployment target/service/database/domain identity is explicit; prevents publication to wrong target. | Prompt → DURABLE AUTHORITY + RELEASE / SETTLE; release target owns publication identity. | M/S/A: YES | Target IDs and allowlists bound to candidate; reject missing or conflicting target. | Promotion/deployment receipt and wrong-target denial. | CL-10, CL-18, CL-26 | P1 |
| CL-13 | Credential references are authoritative references, never model-generated secrets; prevents credential substitution/leakage. | Prompt/secret naming → DURABLE AUTHORITY + ORCHESTRATION; secret manager reference is machine-controlled. | M/S/A: YES | Allowlisted credential reference IDs only; resolve at execution boundary; redact values; reject literals/placeholders. | Reference-only audit, secret non-disclosure test, resolution receipt. | CL-04, CL-10, CL-11, CL-21 | P0 |
| CL-14 | Known authoritative values cannot be replaced by placeholders; absent authority stops. Prevents `<ACCOUNT_ID>`, example values, or invented identity. | Prompt validator → ORCHESTRATION + INDEPENDENT VERIFICATION; orchestration blocks before action, verification catches escaped output. | M/S/A: YES | Canonical value injection from resolver; placeholder/example detector; semantic equality check; fail closed on absent value. | Account/tenant/repo/region placeholder corpus, pre-inference block, post-output rejection. | CL-04–CL-13, CL-30 | P0 |
| CL-15 | Ambiguous authority produces STOP (`AUTHORITY_AMBIGUOUS`); prevents guessing among candidates. | Model judgment → ORCHESTRATION; only orchestration can stop the run before execution. | M/S/A: YES | Candidate cardinality must equal one; conflict is terminal blocked state, never “best effort.” | Two-candidate and conflicting-source tests with durable blocked state. | CL-03, CL-04 | P0 |
| CL-16 | Missing required authority produces fail-closed STOP; prevents invention/default/anonymous execution. | Prompt → ORCHESTRATION + DURABLE AUTHORITY. | M/S/A: YES | No default identity; typed missing-authority error; no tool/provider call after failure. | Missing-field test and call-seam assertion showing zero side effects. | CL-04, CL-14, CL-15 | P0 |
| CL-17 | Operational context is immutable for a unit unless a governed transition occurs; prevents identity drift mid-run. | Model/harness memory → DURABLE AUTHORITY + ORCHESTRATION. | M/S/A: YES | Context version/digest on every unit; transition requires new authoritative resolution and requalification. | Before/after context trace and unauthorized mutation denial. | CL-04, CL-23, CL-24 | P0 |
| CL-18 | Model qualification/routing selects minimum sufficiently capable qualified model for highest risk; prevents convenience routing and underpowered execution. | Model self-selection → ORCHESTRATION; GACM owns route/qualification policy. | M/S/A: YES | Versioned risk dimensions, qualification registry, deterministic route decision, approval/budget constraints; model cannot qualify itself. | Route receipt, qualification identity, escalation and underqualification tests. | CL-19, CL-20, CL-23 | P0 |
| CL-19 | Luna/Terra/Sol escalation is governed and monotonic by risk; prevents model choosing a cheaper/inadequate route. | Prompt/model preference → ORCHESTRATION. | M/S/A: YES | Risk-to-route policy, minimum capability threshold, escalation on ambiguity/blast radius/architecture/authority risk; no downward self-downgrade. | Boundary corpus for Luna→Terra→Sol and route-policy version proof. | CL-18, CL-20 | P0 |
| CL-20 | Model identity and provider route are recorded and cannot be silently substituted; prevents wrong model/provider evidence. | Model output metadata → DURABLE AUTHORITY + ORCHESTRATION. | M/S/A: YES | Bind provider/model/config revision to unit and evidence; reject missing or mismatched receipt. | Model route receipt and substituted-provider negative test. | CL-18, CL-23, CL-33 | P1 |
| CL-21 | GCU executes only within a governed unit and cannot exceed permission/surface boundary; prevents unrestricted agent changes. | GCU prompt/tool convention → EXECUTION / GCU wrapped by ORCHESTRATION. | M/S/A: YES | Capability token or equivalent scoped permissions: repo/ref/worktree, allowed paths, tools, budgets, time, network, credential refs; deny by default. | Tool authorization receipts, forbidden-path/tool/network tests. | CL-08, CL-09, CL-22, CL-23 | P0 |
| CL-22 | Writable surfaces are explicit and protected surfaces are denied; prevents unrelated or destructive edits. | Prompt “stay in scope” → EXECUTION / GCU. | M/S/A: YES | Allowlist writes, protected-file policy, diff guard, no undeclared file creation; require governed reopen for expansion. | Attempted out-of-scope/protected writes and exact diff proof. | CL-21, CL-24, CL-31 | P0 |
| CL-23 | Each bounded work unit has input state, outcome, surfaces, model, risk, tests, stop conditions, and evidence; prevents long-run drift. | Model planning → ORCHESTRATION + DURABLE AUTHORITY; orchestration freezes the contract. | M/S/A: YES | Versioned unit contract; execute only if all required fields are present and candidate/context digests match. | Unit record and malformed/expired contract rejection. | CL-01, CL-04, CL-18, CL-21 | P0 |
| CL-24 | Failure diagnosis and repair classification are evidence-based; prevents casual scope claims and repeated blind repair. | Execution agent judgment → INDEPENDENT VERIFICATION + ORCHESTRATION. | M/S/A: YES | Require causal boundary, affected scope, dependency graph, and repair class from non-executor analysis; three-attempt reset. | Diagnostic record, reset after three same-root attempts, falsification tests. | CL-21–CL-23, CL-27–CL-29 | P0 |
| CL-25 | Local repair reruns affected unit plus dependent tests, not unrelated passed units; prevents unnecessary full reruns and stale assurance. | Model decides rerun set → ORCHESTRATION + INDEPENDENT VERIFICATION. | M/S/A: YES | Machine-derived dependency closure and affected test set; prior independent units remain valid only if dependencies unchanged. | Scope calculation receipt and regression proving unrelated unit is not rerun. | CL-24, CL-27, CL-28 | P1 |
| CL-26 | Architecture-bearing, authority-bearing, model-bearing, security, shared-schema/config, verification-infrastructure, or high-blast-radius repair triggers broader requalification; prevents unsafe local repair. | Executor decides “small” → ORCHESTRATION policy + INDEPENDENT VERIFICATION gate. | M/S/A: YES | Typed trigger list, dependency/blast-radius analysis, mandatory broader gates; executor has no override. | Trigger matrix tests for each category and blocked bypass attempt. | CL-18, CL-24, CL-25, CL-29 | P0 |
| CL-27 | Dependency/blast-radius determination is explicit and reproducible; prevents hidden consumers escaping verification. | Model graph intuition → DISCOVERY / GRAPH for candidate discovery, ORCHESTRATION for authoritative decision. | M/S/A: YES | Build dependency evidence from approved sources; resolve material facts to authority; freeze affected-scope set. | Dependency graph provenance, consumer inventory, changed-scope receipt. | CL-02, CL-03, CL-24–CL-26 | P0 |
| CL-28 | Independent verification evaluates outcome, scope, regressions, authority, identity, forbidden changes, tests, artifact/deployment identity; prevents false PASS. | Executor/self-test → INDEPENDENT VERIFICATION. | M/S/A: YES | Separate verifier context/process and typed `PASS/FAIL/BLOCKED/UNOBSERVABLE`; no executor write to verification decision. | Independent verifier receipt tied to exact candidate and negative false-PASS tests. | CL-21–CL-27, CL-33 | P0 |
| CL-29 | Executor cannot issue authoritative final PASS; prevents self-certification. | GCU report → INDEPENDENT VERIFICATION. | M/S/A: YES | System rejects executor PASS as release state; only verifier can emit authoritative PASS. | Self-PASS attempt rejected; role separation and audit log. | CL-28, CL-31 | P0 |
| CL-30 | Output validation verifies authoritative identity and forbidden placeholders at the boundary; prevents escaped wrong-account/placeholder artifact. | Model prompt/output prose → INDEPENDENT VERIFICATION + ORCHESTRATION. | M/S/A: YES | Validate structured outputs against context digest, allowed values, placeholder patterns, and target contract before persistence/publication. | Account failure-class end-to-end corpus and mismatch artifact rejection. | CL-05–CL-17, CL-14, CL-28 | P0 |
| CL-31 | Run state is durable and reconstructable without chat memory; prevents continuation drift and unverifiable resume. | Chat/harness memory → DURABLE AUTHORITY + ORCHESTRATION. | M/S/A: YES | Persist run/unit IDs, PRD/candidate identity, context, route, inputs/outputs, tests, failures/repairs, scope, verification, human actions, promotion/deploy/settle/rollback. | Kill/reload/new-chat reconstruction test with identity equality. | CL-01, CL-04, CL-17, CL-23, CL-33 | P0 |
| CL-32 | Continuation across chats/sessions requires durable state, not conversation authority; prevents stale or reconstructed plan use. | Chat context → DURABLE AUTHORITY. | M/S/A: YES | Resume only from persisted run state; reject absent/stale/mismatched state and require governed re-resolution. | Session-loss/restart test and stale-state rejection. | CL-31, CL-17 | P0 |
| CL-33 | Every material identity has continuity entry→auth→service→persistence→reload→job/provider→consumer→render/publication→terminal result; prevents substituted/dropped identity. | Ad hoc logs/SHAs → ORCHESTRATION + DURABLE AUTHORITY, independently verified. | M/S/A: YES | Propagate typed identity envelope and assert equality at each handoff; no default/anonymous/fallback/reconstruction. | Exact production-shaped identity trace and negative wrong-identity run. | CL-04–CL-17, CL-20, CL-31, CL-34 | P0 |
| CL-34 | Promotion is an explicit governed state transition, not an executor action; prevents unapproved release. | GCU/model report → RELEASE / SETTLE + HUMAN JUDGMENT where required. | M/S/A: YES | State machine requires independent PASS, exact candidate, required human authorization, target identity, and promotion receipt. | Promotion denial/approval transition tests and receipt. | CL-28, CL-29, CL-33, CL-36 | P0 |
| CL-35 | Stable rollback authority remains untouched and recoverable; prevents experimental failure from corrupting known-good state. | Process convention → DURABLE AUTHORITY + RELEASE / SETTLE. | M/S/A: YES | Isolated fork/branch/worktree, immutable rollback target, rollback command/state transition, evidence preservation; deny destructive stable writes. | Rollback drill with exact target identity and stable-state comparison. | CL-08, CL-09, CL-22, CL-34 | P0 |
| CL-36 | Deployment/publication identity is distinct from repository SHA; prevents claiming deployment from source identity alone. | Git SHA/prose → RELEASE / SETTLE + INDEPENDENT VERIFICATION. | M/S/A: YES | Record and compare candidate, worker/UI revision, prompt/model config, schema/database state, target; reject missing identity. | Deployment identity receipts and mismatch test. | CL-12, CL-20, CL-33, CL-34 | P0 |
| CL-37 | SETTLE observes released behavior and only then records completion; prevents deployment success being treated as completion. | Deployment status → RELEASE / SETTLE. | M/S/A: YES | `SETTLING/SETTLED/FAILED/UNOBSERVABLE` state machine; high-risk observation outside changed blast radius; no completion before `SETTLED`. | Released-candidate observation tied to deployment identity and failure/unobservable tests. | CL-28, CL-34, CL-36 | P0 |
| CL-38 | Human authority is explicit for decisions reserved to humans; prevents model self-promotion, policy change, or risk acceptance. | Model recommendation → HUMAN JUDGMENT + ORCHESTRATION gate. | M/S/A: YES | Authenticated human actor, decision scope, timestamp, decision digest; no inferred approval from chat silence or model PASS. | Approval/denial audit trail and impersonation/silence tests. | CL-28, CL-29, CL-34, CL-37 | P0 |
| CL-39 | GACM fail-closes on ambiguity, missing authority, unobservable verification, policy/identity mismatch, and stale proof; prevents fabricated success. | Prompt stop instructions → ORCHESTRATION + INDEPENDENT VERIFICATION + RELEASE / SETTLE. | M/S/A: YES | Typed blocked states, no side-effect transitions after block, invalidation on candidate change, durable reason/evidence. | One negative test per fail-closed condition and state-machine invariant proof. | CL-03, CL-15, CL-16, CL-28, CL-31, CL-37 | P0 |
| CL-40 | Pilot exclusions remain excluded: no weights, methodology rewriting, self-promotion of learned policies, unrestricted cross-project learning, Hermes primary engine. | Documentation → GOVERNANCE + EXECUTION / GCU policy guard. | M/S/A: YES | Deny excluded capability/tool/path and require human-authorized methodology change outside Pilot v1. | Capability inventory and attempted-exclusion tests. | CL-21, CL-38, CL-39 | P0 |
| CL-41 | Evidence trail and measurements are complete and reproducible; prevents uncheckable claims about autonomy, cost, interventions, routing, repairs, regressions, rollback, and wall time. | Reports/model narrative → DURABLE AUTHORITY + INDEPENDENT VERIFICATION. | M/S/A: YES | Structured append-only evidence schema with run/unit/candidate identity and required metric fields; reject incomplete closure. | Evidence completeness checker and exact-artifact digest. | CL-23, CL-28, CL-31, CL-33 | P1 |
| CL-42 | Final completion requires all applicable acceptance criteria and no hidden blockers; prevents partial pilot success being called PASS. | PRD checklist/model summary → INDEPENDENT VERIFICATION + RELEASE / SETTLE. | M/S/A: YES | Machine gate evaluates criteria against exact candidate; only verifier/release state can close. | Acceptance matrix, zero open critical/major findings, exact-candidate closure audit. | CL-28–CL-41 | P0 |

## Critical account / authority failure-class test

The failure class “authoritative value exists but the LLM emits a placeholder, asks again, guesses, or uses another account/project” is not safely solved by a prompt. It requires three deterministic barriers:

| Stage | Required controls | Deterministic behavior |
|---|---|---|
| Before inference | CL-01, CL-04–CL-17, CL-23 | Resolve exactly one context, bind it to the unit, inject typed canonical values/references, and refuse to start if missing or ambiguous. The model does not receive an authority-selection decision to make. |
| During execution | CL-21–CL-23, CL-30 | Scope credentials/tools/paths to the resolved identity; prevent literal identity substitution and reject placeholder-bearing structured outputs before side effects or persistence. |
| Independent output verification | CL-28–CL-30, CL-33, CL-39 | Compare every material identity in output/artifact/receipt against the authoritative context and trace equality to the terminal result; emit `FAIL` or `BLOCKED`, never repair the identity silently. |

Minimum acceptance corpus must include: known account + placeholder; known account + user-requested re-entry; known account + second-account guess; known tenant + cross-tenant project; known region + default region; known repository + similarly named repository; and missing/ambiguous authority. Each case must prove zero unauthorized provider/tool calls and durable blocked evidence where applicable.

## Misplaced-control findings

1. **F-01 — Prompt-only authority retrieval is unsafe.** PRD §2 correctly identifies the problem, but any SOP telling the model to “retrieve” account/tenant/repository/region is misplaced. Move resolution to CL-04–CL-17 and retain prompts only as explanation.
2. **F-02 — Model-selected routing is unsafe.** Model qualification and escalation must be orchestration-owned (CL-18–CL-20), with model identity recorded, not inferred from prose.
3. **F-03 — GCU-owned final PASS is prohibited.** GCU may test and report evidence, but CL-28/CL-29 require an independent verifier to own authoritative PASS.
4. **F-04 — Executor-owned repair breadth is unsafe.** “Smallest affected scope” and broader-requalification triggers must be machine-derived from dependency/blast-radius evidence and policy (CL-24–CL-27).
5. **F-05 — Deployment success is not completion.** Promotion and deployment status cannot close a run; SETTLE must own released-behavior observation (CL-34–CL-37).
6. **F-06 — Git SHA alone is insufficient release identity.** CL-36 requires direct identity for each participating deployment/config/schema component.
7. **F-07 — Chat continuation is not authority.** CL-31/CL-32 require durable run state and reject reconstruction from conversation memory.
8. **F-08 — Graphify-derived facts cannot authorize.** CL-02/CL-03 require authoritative re-resolution for every material execution fact.
9. **F-09 — “Fail closed” must be a state-machine invariant.** A prose stop instruction is insufficient; CL-15/16/39 require blocked states with no side-effect transition.

## Missing deterministic controls

The repository currently has no implementation, schemas, tests, or machine gate. The following are therefore missing and are Phase 2+ prerequisites: authoritative source/ref/digest resolver; exact context schema; identity envelope and continuity assertions; Graphify provenance contract; allowlisted credential reference resolver; placeholder validator; qualified model registry/router; scoped GCU capability boundary; bounded-unit schema/state machine; dependency/blast-radius engine; independent verification process and role boundary; durable run state/recovery; promotion/rollback/SETTLE state machines; deployment identity receipts; fail-closed machine gate; evidence completeness and exact-candidate staleness checks; and permanent negative-path regressions for the account failure class.

No application implementation was performed in this Phase 1 run. These are audit findings and prerequisites, not implemented features.

## Control ownership map

| Layer | Owns | Must not own final authority for |
|---|---|---|
| BUSINESS | Desired outcome, risk appetite, product acceptance intent | Technical identity, execution permission, PASS |
| GOVERNANCE | Frozen methodology, exclusions, policy versions, required gates | Runtime guesses or hidden state |
| DURABLE AUTHORITY | GitHub state, approved identities, refs, durable run records, rollback target | Discovery-only relationships; model interpretation |
| DISCOVERY / GRAPH | Relationship/source discovery and dependency candidates | Authority, authorization, final affected scope without authoritative proof |
| ORCHESTRATION | Context resolution, unit freezing, routing, permissions, transitions, fail-closed behavior, repair/requalification policy | Independent PASS, human-only approval |
| EXECUTION / GCU | Bounded implementation, local tests, evidence generation within capability scope | Policy override, authoritative PASS, promotion |
| MODEL | Reasoning, diagnosis proposal, implementation proposal, bounded execution output | Identity selection, qualification, permissions, PASS, promotion |
| INDEPENDENT VERIFICATION | Falsification, exact-candidate evaluation, authoritative PASS/FAIL/BLOCKED/UNOBSERVABLE | Changing the candidate to make evidence pass |
| RELEASE / SETTLE | Promotion gate, deployment identity, released behavior, rollback/completion state | Rewriting authority or waiving human policy |
| HUMAN JUDGMENT | Product/risk acceptance and explicitly reserved approval | Delegating deterministic identity/safety controls to model preference |

## Critical dependency relationships

```text
GitHub authority (CL-01)
  ├─ Graphify provenance + re-resolution (CL-02/03)
  └─ exact operational context (CL-04)
       ├─ identity controls CL-05–17
       ├─ unit/permission freeze CL-21–23
       └─ model routing CL-18–20
             ↓
        bounded GCU execution
             ↓
  dependency/blast-radius + repair policy CL-24–27
             ↓
  independent verification CL-28–30
             ├─ durable evidence/reconstruction CL-31–33
             └─ promotion/rollback/SETTLE CL-34–39
                         ↓
                  acceptance/evidence closure CL-41/42
```

The most important non-bypassable chain is `CL-04 → CL-14/16 → CL-21 → CL-30 → CL-33`: resolve identity, prevent placeholders/defaults, constrain action, validate outputs, and prove terminal continuity. A green model output or matching repository SHA cannot replace this chain.

## Phase 2 implementation prerequisites

Phase 2 may begin only after HUMAN PASS on this audit and resolution of B-01. The implementation order should preserve the PRD’s fixed sequence, with these contracts frozen first:

1. authoritative identity/context and source provenance schema, including account/tenant/client/project/repository/branch/environment/cloud account/region/deployment/credential reference;
2. durable run/unit identity and reconstruction schema, with candidate and version digests;
3. fail-closed error/state vocabulary and side-effect transition invariants;
4. Graphify adapter contract that returns provenance but cannot authorize;
5. model qualification/routing/receipt contract for Luna, Terra, and Sol;
6. GCU scoped capability and writable-surface contract;
7. independent verifier role/process and exact-candidate evidence contract;
8. dependency/blast-radius and repair/requalification matrix;
9. placeholder/identity validator with the mandatory negative corpus;
10. promotion/rollback/deployment-identity/SETTLE state machines;
11. machine acceptance gate and evidence completeness checker.

Phase 2 must not install Graphify before the authority/provenance contract exists. Hermes, continual weight learning, autonomous methodology rewriting, and self-promotion of learned policy remain excluded.

## Verification checklist and counts

| Verification | Result |
|---|---|
| Starting SHA matched authorized SHA before work | PASS (`HEAD`, branch, and `origin/main` matched `d5d80587...`) |
| Only Phase 1 audit artifact changed in repository | PASS at audit creation; proof file is outside repository |
| Both authoritative files read first | PASS |
| Every explicit PRD control represented | PASS: PRD §§4–24 traced by CL-01–CL-42 and the prerequisite/findings sections |
| Safety-critical prompt-only controls flagged | PASS: F-01, F-02, F-03, F-04, F-05, F-07, F-08, F-09; matrix marks model/stale/ambiguity bypass risk |
| GitHub remains authority | PASS-PLACEMENT; implementation proof missing |
| Graphify remains discovery only | PASS-PLACEMENT; implementation proof missing |
| Executor cannot self-certify authoritative PASS | PASS-PLACEMENT; implementation proof missing |
| Account/placeholder failure class deterministic prevention | PASS-PLACEMENT; end-to-end implementation proof missing |
| No application implementation performed | PASS |
| Current-state identity consistency | FAIL / BLOCKED: B-01 |

**Matrix count:** 42 controls total; 42 placement decisions recorded; 0 controls omitted from the audit scope; 0 implemented runtime controls claimed; 9 misplaced-control findings; 1 open critical governance blocker (B-01).
**Placement result:** 42 `PASS-PLACEMENT` assignments, subject to implementation proof.
**Implementation/release result:** `BLOCKED` until B-01 and all P0 deterministic prerequisites are resolved.

## Explicit conclusion

**PHASE 1 RESULT: BLOCKED for progression/release; audit artifact complete.**

The audit establishes deterministic ownership for every material PRD control and explicitly rejects prompt-only enforcement for authority, identity, routing, permissions, repair breadth, PASS, promotion, settlement, and fail-closed behavior. It does not authorize Phase 2. Human review is required; after HUMAN PASS and resolution of B-01, Phase 2 may start with the prerequisite contracts above.

**PRODUCTION PATH EQUIVALENCE:** N/A-with-direct-proof — no production execution or release claim was made; this is a pre-implementation control-placement audit.
**PRODUCTION IDENTITY CONTINUITY:** BLOCKED — no runtime path exists yet, and B-01 leaves repository authority identity inconsistent. No production-readiness claim is made.
