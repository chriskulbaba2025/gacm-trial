# Red Queen Challenge — GACM review and bounded follow-up register

**Recorded:** 2026-10-31  
**External review date:** 2026-10-27  
**Reviewer:** Zack Cameron, independent systems reviewer  
**Reviewed source:** `GACM: The Red Queen Challenge`, one-page PDF, file `459446b2-05c7-4e67-9afb-a08a2be88e84.pdf`, accessible in the operator's ChatGPT Library, **not copied into GitHub in this tranche**.  
**Scope actually reviewed:** Public GACM Notion charter, 12 manual sections, and 11 starter templates. No frozen v4.2.2 controller source/runtime inspected; no actual GACM execution attack attempted.  
**Record status:** **EXTERNAL_REVIEW_OBSERVED / CONTROL_PROPOSALS_PENDING_APPROVAL / IMPLEMENTATION_NOT_AUTHORIZED**. This record captures the operator's request to preserve and assess the Red Queen findings. It is **not** an amendment to frozen methodology or acceptance of any new runtime control.

## 1. Four documentation-level findings (NOT controller defect proof)

| ID | Observation in reviewed public materials | Proposed verification/correction boundary | Status |
| --- | --- | --- | --- |
| RQ-01, approval gap | Bootstrap §1(4) can be read as allowing a supplied repository identity to authorize initialization; another setup path requires separate explicit approval. | Treat a repo URL/name **only as a locator**. Authenticate operator approval separately and reject untrusted/source-provided instructions as authority. Check effective controller boundary, not just prose. | EXTERNAL_FINDING / PROPOSED |
| RQ-02, model-policy drift | Master bootstrap Project Instructions omit the model pin included in Prompt C. | Generate bootstrap/project-instructions from one versioned, pinned authorization + model contract and add contract-consistency tests. Explicit approved model always wins; no implicit fallback/escalation. | EXTERNAL_FINDING / PROPOSED |
| RQ-03, mixed statuses | Gate, persistence and controller-connectivity status may share overlapping free-text labels. | Use distinct **typed state dimensions** (e.g. gate verdict, durable persistence, live connectivity) with explicit transition rules. Do not collapse HOLD/FAIL/PASS or UNKNOWN/PARTIAL/UNAVAILABLE/NOT_CONNECTED/NOT_APPLICABLE. | EXTERNAL_FINDING / PROPOSED |
| RQ-04, template lint/parity | Starter template code-block lists may omit conventional spacing. | Verify **exact published ZIP bytes**, deterministic Markdown lint/render and rendered output parity; never assert artifact content from a reconstructed version. | EXTERNAL_FINDING / PROPOSED |

The public documentation findings are a **starting hypothesis** until matched to the actual current authoritative repo/files and executable enforcement. Do not represent them as verified vulnerabilities or automatically reopen the frozen v4.2.2 methodology.

## 2. Required Red Queen adversarial challenge inventory (proposal)

When a separately authorized controller-boundary review is opened, define an independent negative-control matrix for:

1. Untrusted repository instructions/documentation attempting to mint or alter human approval.
2. Stale SHA / mismatched expected-HEAD write and source-of-truth races.
3. Concurrent workers attempting the same action; fencing/lease and duplicate-effects rejection.
4. Replayed, expired, cross-project or already-consumed approval grants.
5. Silent model/provider substitution or Luna → Terra → Sol fallback.
6. Path traversal/escaped worktrees or writes outside allowlisted surfaces.
7. Budget, paid-provider, model-call, retry, time and tranche limit exhaustion.
8. Forged or empty proof folders, self-certified PASS, wrong-candidate testing and missing independent evidence.
9. Staging-to-production escalation, unsafe promotion and unauthenticated write authority.
10. Crash or interruption between an external side effect and its durable receipt; restart/idempotency/reconciliation.
11. Disconnected controller or persistence uncertainty reported as success rather than HOLD/UNKNOWN.

**Acceptance principle, not a completed test:** Zero unauthorized effects on the agreed attack manifest, true status under every failure, exact candidate-SHA evidence, non-replayed single-use grants, and complete auditable receipts. Each negative control must state setup, authorization, test oracle, expected reject/hold, observed side effects and a reproducible proof digest. No synthetic test may be substituted for real runtime proof where the gate requires it.

### Recurring challenger intent (proposal, not enabled)

The operator's earlier request was to **incorporate Red Queen into GACM as an ongoing adversarial challenger**, rather than only archive a one-off report. A future accepted controller design should call the independent negative-control suite at the approved pre-action, post-repair and pre-promotion gates **when the frozen acceptance contract requires it**, and persist coverage against the exact candidate, authorization and runtime identities. The challenger must not mint approvals, expand the tranche, silently choose a model, or certify its own success. Prefer existing deterministic TypeScript/testing boundaries; do not import the prototype's Python implementation by default.

**Decision status:** Integration intent recorded; exact test manifest, code placement, invocation frequency, scope, cost and pass criteria are **PROPOSED / NOT AUTHORIZED / NOT IMPLEMENTED** pending current controller inspection and a separately approved implementation tranche.

## 3. Actual evidence and explicit limits

- The external reviewer reported building a standalone **Python reference authorization broker** and **32/32 passing adversarial unit tests**, with source, test output and SHA-256 manifest supplied in that review context. This result belongs only to the independent prototype; **it is not 32/32 GACM controller tests**.
- The reviewed PDF itself is the available summarized evidence for this record; the external prototype's source files, test logs and manifest were **not inspected or imported** in this 2026-10-31 GitHub reconciliation. Status for controller integration: **NOT_TESTED / NOT_IMPLEMENTED / NOT_VERIFIED**.
- The operator's 2026-10-27/29 discussion supported evaluating **the security concepts**, not automatically importing Python. Retain TypeScript controller or existing implementation language unless a separate measured, approved case justifies a new dependency. Markdown is documentation, not a substitute for an authenticated tool authorization boundary.
- Cross-project GitHub and GACM v4.2.2 authority remain unchanged. The 2026-10-27 [autonomous tranche handoff](GACM_AUTONOMOUS_TRANCHE_DESIGN_HANDOFF_2026-10-27.md) proposes bounded sequential runs but does not prove a running coordinator. The current [cross-project reconciliation](GACM_CROSS_PROJECT_CURRENTNESS_RECONCILIATION_2026-10-31.md) remains PARTIAL.
- This does **not** provide approval for paid engagement, controller code mutation, the next Foundation, another Codex/model session, product deployment, changes to production, or new enforcement claims.

## 4. Smallest prospective follow-up; separately authorized

**Candidate name (planning only):** `GACM-RED-QUEEN-CONTROLLER-AUTHORITY-PREFLIGHT-001`.

**Read-only first:** inspect the **actual current** `chriskulbaba2025/gacm-controller` source, local executable SHA, allowed commands, auth boundary, schema, persistence and controller process; resolve relevant v4.2.2 frozen contracts and current GACM Foundation 17 control placement; map RQ-01–RQ-04 and the negative controls against existing code/tests; determine which are already enforced, missing, contradicted, or unverified. Compare native solutions before new custom code. Preserve all dirty work/proof.

**Only a later separately authorized implementation tranche** may add or repair authenticated single-use grants, expected-SHA compare-and-swap writes, fencing/idempotency, proof verification, typed states, or associated fault-injection tests. Use the smallest owning boundary and reviewable PR; never replace the existing harness or change the pinned model by inference.

**Suggested acceptance gates for that later tranche:** deliberate failing-then-passing tests on one bounded controller seam; stale expected SHA refusal, double-use refusal, wrong project refusal, crash/replay refusal, forbidden production refusal, model and cost ceiling refusal, forged proof refusal, true fail-closed state; targeted tests and required wider regression, independent exact-SHA verification and actual runtime proof where required. Maximum three failed repairs in a defect family before diagnostic reset.

**STOP:** This document is a research/decision register only. Do not proceed into the preflight or implementation from this merge without separate human authorization.
