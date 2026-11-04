# GACM Expert Pre-Execution Prompt Quality Gate v1

**Gate ID:** `GACM-EXPERT-PREFLIGHT-V1`
**Status:** ADDITIVE GOVERNANCE CONTRACT; execution/runtime enforcement requires independent proof
**Effective boundary:** GACM-owned prompt generation and governed task execution only, following explicit adoption by the owning runtime
**Authority:** Current human-approved objective, scope, source-of-truth, model, provider, cost/budget, retries, tranche, environment, production, and approval controls always take precedence.

## Purpose

For a substantive governed task, get the depth of a domain expert **without increasing the authorized work**. Identify missing checks, original evidence, proven methods, independent verification, and material risks before editing code, calling a provider, or changing a system. This is a pre-execution *review*, not permission to expand the objective or run more tools/models.

## Order and required review

1. **Freeze and reconcile authority.** Identify the real current project/repository/file and its branch/SHA, exact tranche, allowed paths, environment, production boundary, model/provider, budget and retry/approval limits. Do not reconstruct authoritative state from conversation memory, summaries, or prior handoffs.
2. **Expert omission check.** State the material checks a qualified practitioner would make that the user did not explicitly request. Mark them as OBSERVATIONS unless already in the authorized acceptance contract. Do not automatically perform added work.
3. **Raw source check.** Identify the primary materials actually governing this task (current files, original records, first-party provider responses, contract, logs, authoritative documentation), with freshness and provenance. Use the smallest relevant slice. A missing or inaccessible source is UNKNOWN/UNAVAILABLE, never assumed negative.
4. **Methods and tools check.** Diagnose root cause/owning boundary, dependencies and blast radius before coding. Compare relevant native capabilities, current official documentation, established maintained solutions, templates and proven patterns before proposing custom work. Discovery is read-only and obeys all tool/network/model/cost constraints.
5. **Independent acceptance check.** Specify how an independent observer or deterministic test can verify the original outcome using the frozen contract, exact identity and required evidence. Executor prose, a new checklist, or a rewritten prompt is not acceptance proof.
6. **Risk and decision check.** Name material failure modes, information gaps, authority conflicts, scope drift and production effects. If any finding requires a materially different task, expense, retry, model, provider, environment or approval, **HOLD and request explicit authority**; do not silently enlarge the run.

## Application to prompts

- Every **new GACM execution prompt** must include or reference this preflight in the prompt actually delivered to the executor, not only in a README.
- Apply it once per governed execution boundary, before material actions; reuse valid receipts across unchanged steps and resumes. Do not add repeated paid model calls, redundant diagnostics, unnecessary searches or boilerplate.
- Intent classification, status queries and trivial read-only operations do not need an expert-analysis run; use `NOT_APPLICABLE` with the reason when a receipt is required.
- Keep the user's original objective and every hard constraint verbatim in authority. The expert check may suggest omissions; it may not rewrite the authorized work, create a new tranche, or grant execution permission.
- For missing material inputs, return `HOLD` with the smallest exact blocker. Do not ask an unnecessary question when the current approved evidence already resolves it.
- The review never overrides existing GACM authority, credential provenance, provider, generalization, verification, settlement or production gates.

## Minimal preflight receipt

For a nontrivial governed task, the execution proof should record these concise fields before implementation:

```text
EXPERT_PREFLIGHT: REVIEWED | HOLD | NOT_APPLICABLE | NOT_VERIFIED
SOURCE_OF_TRUTH: repository/file/ref/SHA or UNAVAILABLE
EXPERT_OMISSIONS: material observations only; no added authorization
RAW_EVIDENCE: primary sources used or explicit gap
METHOD: chosen existing/native approach and why; or bounded discovery HOLD
ACCEPTANCE: independent evidence required by the original frozen contract
RISKS: owning boundary, dependencies, failure modes and blast radius
SCOPE_CHANGE: NONE | NEEDS_HUMAN_AUTHORITY
```

`REVIEWED` means the review was recorded, **not** that the task, quality, controller, or deployment has passed. It cannot authorize execution independently. Absence of the receipt on a material governed task is `NOT_VERIFIED` and prevents claiming this gate is enforced. A `HOLD` never changes to `REVIEWED` solely because an executor writes that it did.

## Enforcement and proof boundary

A compatible prompt builder must inject these instructions in every GACM-governed execution prompt; a targeted test must render an actual representative prompt and assert the contract is present and scope-preserving. Runtime acceptance must verify the installed controller's exact SHA, generated prompt/proof receipt and a negative case that blocks unauthorized expansion. GitHub docs, source tests and PR checks do **not** prove that the user's locally running controller adopted a change. Until separately tested, runtime enforcement is `NOT_VERIFIED`.

This contract is additive to frozen GACM methodology, requires no external model escalation, and creates no standing cross-project mutation authority.
