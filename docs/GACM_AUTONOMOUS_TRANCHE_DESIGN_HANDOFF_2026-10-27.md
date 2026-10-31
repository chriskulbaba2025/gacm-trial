# GACM — Autonomous Tranche Operating Model: Conversation Handoff

**Recorded:** 2026-10-27
**Status:** PLANNING MEMORY / PROPOSED DESIGN / NOT APPROVED IMPLEMENTATION / NOT VERIFIED RUNTIME
**Owner:** Human GACM operator
**Intent:** Preserve the decisions and unresolved facts from the 2026-10-27 architecture discussion for the next governed tranche.
**Authority:** This file is a non-authoritative planning note. It does not modify GACM v4.2.2, accepted Foundation contracts, controller settings, production permissions, or a frozen tranche. Approval and verified current source always outrank this note.

## 1. Requested outcome

GACM should complete an entire explicitly approved, bounded tranche with minimal human intervention:

1. Human defines and approves one tranche and its constraints.
2. GACM reads current authoritative project and runtime identities, freezes product-level success conditions and evidence.
3. GACM checks proven internal patterns and searches relevant official documentation, native platform features, templates, maintained open-source solutions, and previous implementations **before proposing custom code**.
4. GACM identifies root causes, owning boundaries, blast radius, and shortest reliable solution bridge; it compares alternatives, cost, licensing, and compatibility.
5. Existing governed controller launches Codex with the explicitly pinned model (operator preference: **GPT-5.6 Luna Medium for external Codex execution**, unless separately authorized otherwise).
6. On each bounded Codex run, GACM gathers actual output, errors, changed-file identity, receipts, and verification evidence.
7. A durable coordinator diagnoses remaining within-tranche work, either stops with the truthful status or launches a **sequential** follow-up Codex run within the SAME approved tranche and its fixed budget/retry/scope constraints.
8. Repeat until the frozen complete outcome passes every required independent gate, or a genuine blocker / budget / authority / retry limit ends the loop.
9. Present progress, report, evidence and next decision in a simple interface; persist confirmed lessons and defect-family evidence for future work.

**Not desired:** repeated user prompts, manual transfer of Codex reports, patchwork fixture-level repairs, unbounded agent spawning, automatic model changes, silently broadened scope, or unauthorized production/deployment.

## 2. Explicit workflow and authorization constraints

- One tranche = one authorized execution boundary. Internal *sequential* Codex iterations may be automated only if the approved tranche explicitly includes them and specifies upper bounds. No automatic next-tranche approval or progression.
- No parallel/child agents or additional model sessions unless explicitly authorized. Never auto-escalate Luna -> Terra -> Sol or change model.
- Preserve the exact authorized project, environment, repository, branch/SHA, workspace, model, cost, retry count, time bound, allowed paths, forbidden paths, and acceptance contract. Material drift => HOLD/new authorization.
- Production is read-only by default. No publishing, deployment, merge, push or irreversible action beyond separate explicit authorization.
- Diagnose owning boundary/root cause, related failures and blast radius before changing code. Generic repair, not hard-coded examples. At most three failed repairs in a defect family before resetting diagnosis.
- Use targeted tests while repairing. Run broader regression only when required by governing gates or a materially changed candidate. Do not claim PASS without exact-candidate independent proof and real runtime/browser proof where required.
- Preserve status distinctions PASS / FAIL / HOLD and UNKNOWN / PARTIAL / UNAVAILABLE / NOT_CONNECTED / NOT_APPLICABLE. Missing data is not a negative result or zero.
- Continuous improvement produces evidence-linked **proposals**; learning cannot silently mutate governance or approve itself.
- Cost ceiling: default to user's existing ChatGPT planning experience and Codex subscription allowances where eligible; no new API/model/provider charges unless explicitly authorized and metered. Record estimated versus billed costs separately.
- No Desktop Commander dependency or redundant controller installation.

## 3. Two new mandatory preflight concepts

### A. Outcome-Backward Planning — prove before building

Before choosing implementation, freeze the *complete* product definition of done, source/target parity, invariants, negative controls, exact evidence needed, affected dependencies, and what must remain unchanged. The existing GACM Foundation 13 whole-system/generalization contract already covers much of this; reuse and enforce its existing boundary instead of duplicating it.

### B. Solution Discovery First — reuse before rebuilding

Search and compare existing platform-native capabilities, official supported tooling, established starter templates, maintained libraries, proven code and historical patterns. Include compatibility, security, license, change scope, cost, maintenance and actual suitability. The output is a traceable candidate decision; discovery is not execution authority. For trivial tasks a small deterministic lookup may suffice; for architectural changes the comparison is larger.

**Example:** A Sanity website migration should have discovered supported Sanity Studio/Presentation/Visual Editing patterns, asset migration tooling, native content structures and template strategies before proposing custom conversion work. Frozen acceptance must include all content, images, interactions, edit persistence, draft isolation, and original design parity.

**Important distinction:** Existing Graphify discovery in GACM finds project/code relationships. It is not a verified external web solution search; do not conflate the two.

**Proposed approval input:** a versioned preflight package containing objective, authoritative-source identity, outcome/evidence matrix, solution candidates/sources/currentness, alternatives and decision, risks, estimated cost, frozen model/scope/budget, test/stop contract, and human authorization reference. The preflight report must be checked at the actual execution boundary; a prompt-only reminder is insufficient for material safety rules.

## 4. Proposed autonomous coordinator

Conceptual states (not current implemented GACM states):

`INTAKE -> AUTHORITY_VERIFIED -> OUTCOME_FROZEN -> DISCOVERY_REVIEWED -> PLAN_APPROVED -> RUNNING -> RECEIPT_CAPTURED -> INDEPENDENT_VERIFICATION -> (CONTINUE_SAME_TRANCHE | ACCEPTED | HOLD | FAIL)`

- Reuse existing controller execution/authority and evidence machinery. First establish actual current local runtime SHA and preserve dirty/unmerged work.
- Coordinator must be durable, restart-safe, idempotent for side effects, crash/reconciliation-safe, and bound to an immutable tranche ID/contract digest. Prevent duplicate actions after uncertain interruption.
- One active Codex run at a time, sequential retries only; avoid unbounded loop, duplicate tests and accumulating context.
- The decision to continue must be based on structured independent evidence, not Codex claiming `DONE`, a report's existence, or a proof-folder path alone.
- Detect unchanged failure signatures, repeated false fixes, scope drift, stale Git SHA, cost ceiling, maximum retries, and inadequate proof. Stop with an accurate HOLD/FAIL; never force a PASS to complete the loop.
- On completion emit a human-readable RESULT / BLOCKER / NEXT ACTION report and immutable evidence references. Follow-up *within* a tranche is automatic where approved; the *next tranche* always needs new authorization.

## 5. Interface and ChatGPT reality

**Preferred human interface:** continue high-value diagnosis, reasoning, planning and review here in the existing ChatGPT UI, with a connected GACM tool/plugin where supported. A lightweight web dashboard (potentially Vercel-hosted) can show automatically refreshed progress, receipts, cost, milestones and reports. Telegram remains an optional exception/completion notifier.

**Important limitation:** A local or Vercel server cannot assume it can continuously push new assistant messages into this ordinary ChatGPT thread or use the consumer ChatGPT UI as an indefinitely running unattended reasoning backend. Connected tools can provide status when invoked; the background orchestration loop belongs to the GACM controller/service. Subscription-backed inference in a separately hosted custom website is eligibility-dependent, **not verified for GACM**. Codex subscription authentication and actual metering need verification before cost claims.

**Progress UI:** display evidence-grounded stages and per-unit completion; no invented percentage when the denominator is unknown. Display last receipt, current run, reason for HOLD, retries used/remaining, verified source SHA, next bounded action, and actual/estimated costs.

## 6. Technology selection principles

- **Keep:** GitHub for authoritative, versioned decisions/contracts/source/proof manifests; existing TypeScript controller and Codex executor; existing SQLite persistence work if its current runtime and proof are qualified; Playwright and deterministic validation for real acceptance.
- **Explore, do not automatically install:** Open Policy Agent for authorization, Promptfoo for adversarial evaluations, Sigstore/GitHub attestations for provenance, Langfuse for API trace visibility.
- **Study before adopting:** Temporal's durability semantics (not automatically another runtime/store); Hermes' reusable skill/memory patterns; Paperclip's cost/approval dashboard patterns; Obsidian as optional read-only knowledge UI; Antigravity only as separately authorized executor evaluation.
- **Languages:** No new Python or Rust dependency is required to adopt the two preflight gates or build a TypeScript coordinator. GACM trial already contains Python prototype/harness code; preserve it. Do not rewrite or add languages without measured reasons.
- **Architecture principle:** prefer existing native and maintained solutions, choose the smallest reliable bridge, and keep authority separate from retrieval, reasoning, execution and independent proof.

## 7. Verified GitHub observations from the current read-only inspection

- Governance/early GACM repository: `chriskulbaba2025/gacm-trial`, `main` observed at `c50ba6e5f5382b3460f0ab1de7d508f330ced800`.
- Foundation 13 governance accepted branch: `governance/gacm-graph-foundation-13-repair-planning-20261004`, observed at `3904adb8c46e16e72880106faf13e5f967983afc`. Frozen governance remains unchanged.
- Controller repository: `chriskulbaba2025/gacm-controller`, `main` observed at `6132c1a22ad3d7b88c2ed36bea3ff5d4e37cfc58`; C1 status-integrity branch at `076db8cc67c36d04804ad9563524ad6e3d825156`; Falardeau onboarding feature branch at `0491cbb4c849bb3499da8ccb9e6b6505ea4bee17`. Controller branches diverge; they are not automatically the active local runtime.
- Controller README explicitly says one Codex run is supported, not independently scheduled sequential runs. `src/core.ts` owns `startCodexRun()` and governed prompt launch; `src/telegram-controller.ts` performs proposals/confirmations and starts the run.
- Existing Controller Codex launch uses `sandbox_workspace_write.network_access=false`. External solution discovery therefore must occur in a separately authorized read-only discovery context before offline execution or through an approved research integration.
- Foundation 12 already describes a deterministic PRD/tranche candidate projection; it does not grant execution authority. Foundation 13 already contains a pre-execution generalization/definition-of-done gate. Reuse, do not duplicate.
- The user reported SQLite persistence experiments and later implementation work; **current installed/durable runtime acceptance is not proven by this GitHub note**. No claim that any new autonomous coordinator exists or is running.
- The Red Queen review supplied an independent Python authorization prototype with 32/32 adversarial unit tests, **not tests of GACM controller**. Its principles can be integrated without importing Python.
- This GitHub scan is source inspection only: local controller identity, dirty worktree, installed services, current authentication, active process, browser session, and end-to-end acceptance were not verified.

## 8. First bounded step proposed for separate authorization

**Candidate tranche:** `GACM-AUTO-LOOP-PREFLIGHT-001` — read-only source/runtime qualification and minimal integration design ONLY.

Requested results:
1. Reconcile which actual controller source/branch/SHA is running; inspect current state, C1 and Falardeau candidate, preserving dirty worktrees and proof.
2. Map existing planning/approval, Codex launch, status persistence/recovery, evidence, and test-entry boundaries.
3. Register already-supported components versus verified missing parts: preflight contract, external solution research, autonomous sequential scheduling, receipt reconciliation, progress feed, cost accounting, lesson storage.
4. Define the smallest owning-boundary implementation and acceptance tests, including crash injection, stale SHA, unapproved next tranche, false PASS, unauthorized cost/model/production, loop budget exhausted, blocked browser, and two real repair iterations in one approved tranche.
5. Propose subsequent implementation tranche boundaries **without executing them**. No production, merges, provider calls, deployments, unapproved model costs, or code changes under the preflight.

**Future implementation acceptance (NOT proven yet):** A realistic bounded project runs at least two sequential Codex iterations under one approval; survives interruption with no duplicated effects; independently checks exact candidate and product outcome; returns truthful PASS/HOLD/FAIL; shows real progress; preserves evidence and model/cost constraints; does not start another tranche.

## 9. Measures of improvement

First-attempt independent acceptance, repeat-defect rate, human interventions per accepted job, number of runs per accepted tranche, verified cost per completed job, mean time to recover, unauthorized attempts rejected, false PASS in adversarial tests (target zero), and outcome completeness. No unmeasured `25% better` claim.

## 10. Next-chat entry

**Continue GACM from this GitHub planning handoff. First verify current GitHub/local controller state and the frozen authority contracts. Do not treat this note as implementation approval. Prepare the smallest read-only preflight tranche to map integration boundaries before changing code. Preserve Luna Medium and all current scope/cost/production/tranche controls. The strategic objective is one human-approved tranche automatically coordinated across bounded sequential Codex runs, with evidence-grounded progress and autonomous within-tranche analysis, repair, recovery and closure.**
