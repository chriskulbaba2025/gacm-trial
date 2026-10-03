# GACM MVP Authority Manifest v1

**Status:** FROZEN CANDIDATE AUTHORITY FOR MVP CLOSURE
**Captured:** 2026-10-03
**Purpose:** Establish one reproducible authority set before additional GACM MVP implementation or promotion.

## Core rule

Internal consistency is not authority. Chat memory, local availability, prior reports, and historical PASS claims cannot replace current source identity.

Every governed closure run must resolve this manifest against live repository state before execution.

## Authoritative identities

| Authority | Repository / ref | Frozen identity | State |
|---|---|---|---|
| GACM governance | `chriskulbaba2025/gacm-trial` / `main` | `786313066f3623806fd477dd12d183be1242699d` | governing baseline |
| GACM closure candidate | `governance/gacm-mvp-closure-00-20261003` | must be resolved from Git after this tranche commit | candidate only |
| Qualification app baseline | `chriskulbaba2025/gacm-qualification-sandbox` / `main` | `8f070ff4419c2d0318356b13f656bf4f0de21021` | current remote main |
| Recovered Human CRIT MVP candidate | `candidate/phase16-human-crit-mvp` | `132cff6d3280e3fe8f86b23a0113cab986df03e3` | recovered candidate; not promoted |
| SPEC | `chriskulbaba2025/spec-skill` / `main` | `30bfb0e78bab11c1e20cdc74b45530114c431654` | upstream authority |
| CRIT | `chriskulbaba2025/crit-universal-skill` / `main` | `187b7f7d3d63025f98386da09255942d6693303d` | upstream authority |

## Recovered candidate proof

The recovered Human CRIT MVP candidate was re-verified on 2026-10-03:

- local HEAD exactly matched `132cff6d3280e3fe8f86b23a0113cab986df03e3`;
- branch was `candidate/phase16-human-crit-mvp`;
- tree was clean before and after regression;
- current `origin/main` was `8f070ff4419c2d0318356b13f656bf4f0de21021`;
- candidate is one commit ahead of that baseline;
- full local regression: **108 tests passed, 28 subtests passed**;
- the exact candidate ref was restored to the remote repository.

This proves recoverability and local regression identity. It does not by itself prove staging, production, release currentness, browser acceptance, independent verification, or SETTLE.

## Candidate scope actually present

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

## Known currentness facts

- `gacm-trial/main` contains governance work later than the historical Phase 14 state recorded in the pre-reconciliation `CURRENT_STATE.md`.
- The recovered Human CRIT candidate was previously local-only and is now preserved as a remote candidate branch.
- The recovered candidate has not been promoted to qualification-app `main`.
- GACM `main` is not branch-protected as of this authority freeze.
- No production mutation is authorized by this manifest.

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

This manifest authorizes reconciliation and proof only.

It does not authorize:

- merge to GACM `main`;
- promotion of `132cff6d...` to qualification-app `main`;
- staging deployment;
- production deployment;
- provider/model substitution;
- V2 implementation.

Promotion requires the GACM MVP Closure Contract, exact-head verification, release-currentness proof, and explicit human promotion authority.

## Fail-closed rule

If any frozen identity differs from live source truth at execution time:

`STATUS = HOLD`

Do not silently update this manifest, infer a replacement candidate, or continue from memory.
