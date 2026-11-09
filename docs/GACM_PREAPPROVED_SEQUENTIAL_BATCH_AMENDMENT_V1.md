# GACM Pre-approved Sequential Batch Amendment v1

**Status:** ADDITIVE CANDIDATE — not merged; does not authorize any actual batch execution.
**Scope:** GACM governance and the existing `gacm-controller`. Preserve frozen GACM v4.2.2, accepted Foundations, execution recipes, and release gates.

## 1. Narrow exception: multi-tranche pre-approval
One tranche remains one immutable execution authority. An authenticated human may approve, in advance, a finite ordered list of **individually specified tranches** inside one signed batch envelope. This permits *scheduling already-approved work*, not creating new authority, tasks, or models. Earlier single-tranche approvals cannot be interpreted as batch consent.

Every tranche retains its frozen objective, repository/branch/SHA, model/provider, cost/time/retry ceiling, writable/forbidden paths, per-action recipe, dependent candidate identity, verification contract, **GACM_EXECUTION_RECIPE_V1 digest**, and STOP conditions. Human gates for high-risk actions and release operations remain mandatory. The next tranche may start automatically **only after independent exact-candidate PASS** of its predecessor.

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

## 6. Source qualification evidence (2026-11-08, opt-in candidate only)

- Controller repository: `chriskulbaba2025/gacm-controller`; candidate branch `feature/gacm-preapproved-batches-20261108`.
- Current exact accepted source-test candidate: `e55f532133d7d83b130fb5240c428bea5dc34429`.
- Windows and Linux hosted CI passed: [run 42551740321](https://github.com/chriskulbaba2025/gacm-controller/actions/runs/42551740321).
- Tests include three sequential tranches, an intentional failed independent npm verification and automatic repair, same-worktree restart, forged/self-issued PASS rejection, signed approval, and forbidden-path HOLD. Codex was simulated; no model/provider calls.
- Operator-facing native CLI: `npm run batch:run -- <absolute-signed-plan.json>` and `npm run batch:status -- <project> <batchId>` from the verified existing controller worktree. The batch requires an independently signed human approval and frozen per-action execution recipes.
- **Not qualified:** installed Windows process identity, authenticated real Codex session, signed live plan, project-specific acceptance/browser, promotion or production. No merge, deployment, installed-controller switch or next-tranche authorization is implied.


## 7. Authoritative C1 reconciliation (2026-11-08, superseding source selection)

The real installed Windows controller was observed on `c1/status-integrity-20261014` at commit `076db8cc67c36d04804ad9563524ad6e3d825156`. This contains 12 unique commits relative to main, so the earlier main-based batch candidate `e55f532133d7d83b130fb5240c428bea5dc34429` **must not be installed over the C1 controller**.

The replacement integration is constructed directly on the installed C1 commit, retaining C1's status-integrity, SQLite, Telegram, workspace and progress contracts.

- Controller candidate branch: `feature/gacm-batches-c1-reconciled-20261108`.
- Exact source candidate: `626d42c72374f3e5b565fa29ae859430353ecbd5`.
- Source relationship: C1 baseline +16 commits, behind 0, changed files 14; no C1 code removed.
- Exact-candidate GitHub Actions Windows and Linux: [PASS run 42554081180](https://github.com/chriskulbaba2025/gacm-controller/actions/runs/42554081180).
- Batch execution used simulated Codex only, real local Git and native `npm run` checks. C1 status contract, workspace and Telegram selftests PASS on hosted CI. C1 integrated launch test requires actual `C:\\Users\\kulba\\Desktop\\telegram-control-sandbox`; this is **NOT_APPLICABLE on hosted runners** and remains an installed-runtime gate.
- Activation is permitted only after exact installed C1 branch/SHA, clean and idle state, model authentication, candidate SHA, targeted local tests and rollback identity are independently checked. Source CI alone does not establish Windows activation or a real Codex batch.
- Previous section 6 records historical qualification of the main-based candidate and is superseded for this specific installed C1 controller. It must not be taken as installation authority.

**Status:** Source integration PASS; installation HOLD until local proof. Governance branch not merged; production and original C1 branch unchanged.
