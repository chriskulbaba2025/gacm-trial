# GACM | Governed AI Change Management

**Primary governance repository:** `chriskulbaba2025/gacm-trial`
**Authoritative branch for consolidated source:** `main`. Always resolve its live HEAD before work; branch names and this README are not immutable source identity.

## Read first

1. [`CURRENT_STATE.md`](CURRENT_STATE.md) — latest accepted boundary and status, followed by preserved historical records.
2. [`docs/governance/FOUNDATION_17_ACCEPTANCE_20261005.json`](docs/governance/FOUNDATION_17_ACCEPTANCE_20261005.json) — latest recorded Foundation acceptance, exact qualified application candidate and proofs.
3. [`GACM_IMPLEMENTATION_PRD_V1.0.md`](GACM_IMPLEMENTATION_PRD_V1.0.md), [`docs/GACM_MVP_AUTHORITY_MANIFEST_V1.md`](docs/GACM_MVP_AUTHORITY_MANIFEST_V1.md) and the actual frozen v4.2.2 methodology — only approved contracts define execution authority.
4. [`docs/GACM_CROSS_PROJECT_CURRENTNESS_RECONCILIATION_2026-10-31.md`](docs/GACM_CROSS_PROJECT_CURRENTNESS_RECONCILIATION_2026-10-31.md) — dated index of recent Falardeau, GSC, PRYSM, VANTAGE and related project lessons; verify each project's current repository instead of treating the snapshot as current authority.
5. [`docs/GACM_AUTONOMOUS_TRANCHE_DESIGN_HANDOFF_2026-10-27.md`](docs/GACM_AUTONOMOUS_TRANCHE_DESIGN_HANDOFF_2026-10-27.md) — proposed bounded sequential execution, not approved or implemented runtime.
6. [`docs/GACM_RED_QUEEN_CHALLENGE_REVIEW_2026-10-31.md`](docs/GACM_RED_QUEEN_CHALLENGE_REVIEW_2026-10-31.md) — external adversarial findings and proposed recurring challenger, **not validated controller enforcement**.
7. [`docs/GACM_RED_QUEEN_TOKEN_EFFICIENCY_PROCESS_V1.md`](docs/GACM_RED_QUEEN_TOKEN_EFFICIENCY_PROCESS_V1.md) — bounded challenger loop and token-efficiency receipt contract; additive process proposal, not proof of controller enforcement.

## Verified repository status (2026-10-31)

- GACM historical MVP closure is preserved. Accepted Foundation **F17** is recorded in governance with application SHA `e31edc33a0e986427d457673f71a2a048983c722` on a separate sandbox candidate branch. **F18 NOT STARTED**; accepting a Foundation does not promote its application candidate or authorize the next tranche.
- Accepted governance history for Foundations 07–17 merged through [PR #8](https://github.com/chriskulbaba2025/gacm-trial/pull/8). October 27–31 autonomous and cross-project handoffs merged through [PR #7](https://github.com/chriskulbaba2025/gacm-trial/pull/7). The corrected current-state index merged through [PR #9](https://github.com/chriskulbaba2025/gacm-trial/pull/9). Red Queen review merged through [PR #10](https://github.com/chriskulbaba2025/gacm-trial/pull/10). Each is source/history, not proof of a live controller or project runtime.
- Old [draft PR #1](https://github.com/chriskulbaba2025/gacm-trial/pull/1) on `phase15/qualification-graph-methodology` **diverges** from accepted `main`. It was deliberately not merged. Its historical checks do not prove compatibility with F17.
- GitHub governance-regression passed on the post-PR #10 merge SHA `8c29430f76ea62b7e6496751e9011f8f6aaae697`. Any later commit needs its own check. Cross-project runtime/currentness remains **PARTIAL / NOT VERIFIED**, not PASS.

## Separate components

| Scope | Repository | Status limit |
| --- | --- | --- |
| GACM methodology, governance, historical evidence, current-state pointers | [`gacm-trial`](https://github.com/chriskulbaba2025/gacm-trial) | This repository |
| GACM/PRYSM execution controller | [`gacm-controller`](https://github.com/chriskulbaba2025/gacm-controller) | Its **actual installed process, source SHA, durability and autonomous sequential scheduling are not verified** by GACM documentation |
| Qualification application and isolated foundation candidates | [`gacm-qualification-sandbox`](https://github.com/chriskulbaba2025/gacm-qualification-sandbox) | Separate exact-SHA candidate/test authority, not production |

## Non-negotiable operating boundaries

- One explicitly approved tranche, with frozen objective, SHA, environment, model/provider, budget, retry bounds, allowed paths and acceptance evidence; no autonomous next-tranche progression.
- Default external Codex model **preference** is `gpt-5.6-luna` Medium unless the specific tranche says otherwise. Never silently switch, escalate, spawn parallel agents or incur additional provider charges.
- Resolve the real authoritative project files and actual runtime before action. Diagnose owning root cause and blast radius; use read-only solution discovery before custom implementation.
- Generic owning-boundary repairs only; no fixture-target shortcuts, speculative proof, or invented acceptance. Reset diagnosis after three failed repairs in a defect family.
- Targeted tests during repair, then required wider regression and independent exact-candidate proof. Real browser/live acceptance is a separate gate where required.
- **Production read-only** without explicit authorization. No implied publishing, deployment, data writes, credential substitution, model routing or protected-branch mutation.
- Distinguish PASS / FAIL / HOLD from UNKNOWN / PARTIAL / UNAVAILABLE / NOT_CONNECTED / NOT_APPLICABLE. Lack of evidence is not a negative observation.

## Red Queen security direction

The desired ongoing Red Queen *challenger* is a repeatable adversarial acceptance framework for untrusted approval, stale SHA, concurrency, approval replay, forged evidence, model/budget drift, scope escapes, production escalation and interrupted effects. **It is a proposal, not a functioning gate.** The independent Python reference broker reported 32/32 tests; those were *not* tests of the actual GACM controller. Evaluate and reuse concepts in the existing owning architecture, without importing Python, changing models, or starting implementation without a separate authorized tranche.

## Status / next action

**GitHub record consolidation: COMPLETE.** **Whole-system/controller currentness: PARTIAL / NOT VERIFIED.** The next technical step is an authorized read-only comparison of the real controller and application/runtime states against the current exact GitHub SHAs, not a new unbounded implementation run.