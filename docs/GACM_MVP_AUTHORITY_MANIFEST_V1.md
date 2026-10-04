# GACM MVP Authority Manifest v1

**Status:** FINAL MVP CLOSURE AUTHORITY — PRE-PROMOTION
**Captured:** 2026-10-03
**Purpose:** Establish one reproducible authority set before additional GACM MVP implementation or promotion.

## Core rule

Internal consistency is not authority. Chat memory, local availability, prior reports, and historical PASS claims cannot replace current source identity.

Every governed closure run must resolve this manifest against live repository state before execution.

## Authoritative identities

| Authority | Repository / ref | Frozen identity | State |
|---|---|---|---|
| GACM governance | `chriskulbaba2025/gacm-trial` / `main` | `786313066f3623806fd477dd12d183be1242699d` | governing baseline |
| GACM final closure candidate | `governance/gacm-mvp-final-closure-20261003` | resolve from Git at each closure step | candidate; final durable record pending SETTLE |
| Qualification app rollback baseline | `chriskulbaba2025/gacm-qualification-sandbox` / `main` | `8f070ff4419c2d0318356b13f656bf4f0de21021` | current remote main before promotion; protected rollback target |
| Final MVP application candidate | `candidate/mvp-final-closure-20261003` | `32d474fdb8fe0672d826ff434b4bfc94c9537407` | exact-SHA CI PASS; staged deployment `3753fec4-9746-4bef-aa07-7c433d8704f6` SUCCESS; independent verification PASS; promotion pending |
| SPEC | `chriskulbaba2025/spec-skill` / `main` | `30bfb0e78bab11c1e20cdc74b45530114c431654` | upstream authority |
| CRIT | `chriskulbaba2025/crit-universal-skill` / `main` | `187b7f7d3d63025f98386da09255942d6693303d` | upstream authority |

## Historical recovered candidate proof

The recovered Human CRIT MVP candidate was re-verified on 2026-10-03:

- local HEAD exactly matched `132cff6d3280e3fe8f86b23a0113cab986df03e3`;
- branch was `candidate/phase16-human-crit-mvp`;
- tree was clean before and after regression;
- current `origin/main` was `8f070ff4419c2d0318356b13f656bf4f0de21021`;
- candidate is one commit ahead of that baseline;
- full local regression: **108 tests passed, 28 subtests passed**;
- the exact candidate ref was restored to the remote repository.

This proves recoverability and local regression identity. It does not by itself prove staging, production, release currentness, browser acceptance, independent verification, or SETTLE.

## Historical recovered candidate scope

The recovered candidate adds or changes the Human CRIT application path, including:

- deterministic analysis and governed state;
- adaptive human questioning;
- semantic CRIT review boundaries;
- advisory-only fast filtering;
- persistence and reopen continuity;
- PRD gating;
- human disposition;
- generalization-path tests;
- browser/HTTP surfaces and related tests.

Named example content is regression evidence only and is not implementation authority.

## V2 architecture boundary

`GACM_V2_FINAL_ARCHITECTURE_HARDENING_AUDIT.md` records an architecture-specification score of 98.6/100.

That score is not runtime completion.

V2 graph memory, graph-aware CRIT, retrieval, convergence, and related architecture work are outside the recovered MVP closure boundary unless separately authorized.

## Current closure authority and currentness facts

- GACM governance final-closure work is isolated on `governance/gacm-mvp-final-closure-20261003`; `gacm-trial/main` remains unchanged before final durable closure promotion.
- Qualification-app `main` remains `8f070ff4419c2d0318356b13f656bf4f0de21021` before promotion and is the protected rollback target.
- Final application candidate `32d474fdb8fe0672d826ff434b4bfc94c9537407` is preserved on remote branch `candidate/mvp-final-closure-20261003`.
- The deterministic MVP acceptance entrypoint PASSes on that exact SHA: compile PASS; strong/mixed/weak generalization 3/3 PASS; whole-system targeted 87/87 PASS; full regression 136/136 PASS.
- Exact-SHA application CI PASSes on `32d474fdb8fe0672d826ff434b4bfc94c9537407`.
- Railway staging deployment `3753fec4-9746-4bef-aa07-7c433d8704f6` is SUCCESS at that exact SHA; served runtime `git_head` matches; governed graph status PASS; Fast Filter AVAILABLE; Human CRIT READY.
- Fresh live strong/mixed/weak scenarios preserve resolved strengths, material follow-up gaps, and unknown state respectively; weak input remains PRD-gated, while explicit human `PROCEED_WITH_GAPS` authority permits PRD generation/approval without hiding the recorded gap.
- Real Microsoft Edge browser acceptance PASSes on both approved-PRD and weak/unknown states with no request-failure or `REVIEW_UNAVAILABLE` text.
- GACM `gacm-independent-verifier-v1` issued authoritative PASS for the exact final closure delta and reviewed currentness/browser/rollback/production-unchanged outcomes.
- SPEC `main` remains `30bfb0e78bab11c1e20cdc74b45530114c431654`; CRIT `main` remains `187b7f7d3d63025f98386da09255942d6693303d`.
- Production remains untouched.

## Executor authority

Default external Codex execution model for governed MVP closure is:

`gpt-5.6-luna`

Rules:

- no automatic model escalation;
- no model substitution based on availability, cost, or convenience;
- no subagents, child runs, parallel agents, or extra model sessions without explicit human authorization;
- no unbounded retry loops;
- model/provider authority must pass the external-provider gate before any authenticated external action;
- executor output cannot certify its own authoritative PASS.

A different model requires explicit human authorization recorded in durable run state.

## Promotion boundary

On 2026-10-03, after Foundation 06 acceptance, human authority explicitly instructed GACM to continue to the end, stop requesting tranche-by-tranche authorization, and finish the MVP. Within the frozen `GACM_MVP_CLOSURE_CONTRACT_V1.md`, this is standing human authority for the remaining MVP closure sequence: final audit, exact-candidate verification, qualification-app `main` promotion, post-promotion SETTLE, durable closure record, and final GACM closure-record promotion.

This standing authority does not expand the frozen MVP definition of done. It does not authorize production mutation, provider/model substitution, retrieval, graph-aware CRIT, convergence, autonomous learning, or other post-MVP V2 implementation.

Promotion is permitted only if exact-head verification, release-currentness, real runtime/browser acceptance, rollback proof, whole-system/generalization proof, and independent verification are all PASS on the exact candidate. Any mismatch remains HOLD.

## Fail-closed rule

If any frozen identity differs from live source truth at execution time:

`STATUS = HOLD`

Do not silently update this manifest, infer a replacement candidate, or continue from memory.
