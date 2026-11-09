# GACM Pre-approved Sequential Batch Amendment v1

**Status:** ADDITIVE CANDIDATE — not merged; does not authorize any actual batch execution.
**Scope:** GACM governance and the existing `gacm-controller`. Preserve frozen GACM v4.2.2, accepted Foundations, execution recipes, and release gates.

## 1. Narrow exception: multi-tranche pre-approval
One tranche remains one immutable execution authority. An authenticated human may approve, in advance, a finite ordered list of **individually specified tranches** inside one signed batch envelope. This permits *scheduling already-approved work*, not creating new authority, tasks, or models. Earlier single-tranche approvals cannot be interpreted as batch consent.

Every tranche retains its frozen objective, repository/branch/SHA, model/provider, cost/time/retry ceiling, writable/forbidden paths, per-action recipe, dependent candidate identity, verification contract, and STOP conditions. Human gates for high-risk actions and release operations remain mandatory. The next tranche may start automatically **only after independent exact-candidate PASS** of its predecessor.

## 2. Immutable envelope
`GACM_PREAPPROVED_SEQUENTIAL_BATCH_V1` binds the ordered tranche list, approval reference, environment, identity, model `gpt-5.6-luna` with `medium` effort, aggregate executions and time limits, zero new chargeable external-provider spending, and explicit denials of production writes, commits/pushes/merges/deployments/publishing, or subagents. Calculate canonical SHA-256 over the envelope excluding its external approval metadata. Store the exact frozen digest in an independently authenticated, durable human-approval record.

An operator approval for implementing this amendment is **not approval to run a future batch**. Verify approval authenticity, revocation and expiry at each tranche boundary. Never accept a self-declared approver field, arbitrary JSON or Codex output as human permission.

## 3. Required controller behavior
`APPROVAL -> PREFLIGHT -> EXECUTE TRANCHE -> SCOPE CHECK -> INDEPENDENT VERIFY -> PASS/NEXT | FAIL/REPAIR/RETEST | HOLD/STOP`.

An audit is an internal gate, not an automatic terminal step. A FAIL returns to diagnosis and repair within the same authorized tranche. Exceeding three failed repairs in the same family requires resetting diagnosis, not unbounded retries. An authentic HOLD, unresolved identity, stale SHA, failed evidence, approval revocation, budget boundary or unapproved action stops the batch.

Never use Codex's `RESULT: PASS`, a proof file, green CI, successful exit status, or an HTTP 200 as independent product acceptance. A PASS receipt must bind the executor run ID, current candidate digest, frozen verification-contract digest, verifier identity and evidence references. Later changes must independently revalidate earlier accepted tranches on the final candidate.

## 4. Exact workspace and restart safety
Use the existing isolated batch-bound Git worktree, **reused for every tranche**; never provision a fresh empty worktree for each follow-up. Capture all tracked, staged, deleted and untracked changes, prevent symlink/target escapes, enforce current active-tranche changed surfaces, and preserve dirty authorized work. Do not reset, clean, stash, force checkout or silently commit. Record the operation and candidate identity durably before dispatch. A crash with uncertain effects causes HOLD pending exact reconciliation; never blindly replay the operation.

One active agent across single-run and batch endpoints. No parallel agents. Preserve independently accepted evidence separately from model output. No model/provider substitution or implicit additional billing. If subscription authentication cannot be verified, HOLD.

## 5. Release and proof
This amendment does not alter production, authorize release/promotion, or change the accepted Foundation state. New high-risk actions and release steps require their own approvals. The prior `GACM_EXECUTION_AUTHORITY_AND_INFERENCE_STATE_CONTRACT_V1` remains mandatory.

Acceptance requires: signed approval binding and revocation checks; exact local installed-source reconciliation; one-worktree, bounded sequential Codex execution; Git scope gate; independent product/browser checks where applicable; verified prior-tranche currentness; interruption without duplicated effects; negative tests for stale identity, false PASS, provider/model drift, unauthorized paths, chargeable usage, and a three-tranche sandbox test with failure, repair and automatic progression. A controller module test alone is not live acceptance.

**Deployment status:** This feature branch is a source candidate only. Installed Windows runtime, credentials, real browser checks and authenticated end-to-end proof remain separate gates.
