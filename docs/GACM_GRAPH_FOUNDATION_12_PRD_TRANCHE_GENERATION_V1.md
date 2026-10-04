# GACM Graph Foundation 12 — Graph-Governed PRD / Tranche Generation v1

**Status:** AUTHORIZED IMPLEMENTATION BOUNDARY
**Opened:** 2026-10-04
**Governance parent:** `0e0195265dd04cbbc2c4a8572663e824e3639c35`
**Application parent:** `0f8d226b8bb28c90abf57ce5ba4f275df0d875c3`

## Purpose

Foundation 12 adds deterministic graph-governed planning from the current accepted application state.

The graph does not author product truth by itself.

The operating flow is:

`CURRENT HUMAN PRD + CURRENT GOVERNED GRAPH -> DETERMINISTIC PLANNING PROJECTION -> CANDIDATE TRANCHE PACKAGE`

The existing human PRD generator remains authoritative for product content. The graph contributes current governed gaps, approval state, tranche identity, dependency state, and scheduler eligibility.

## Core authority rule

Graph-derived planning is a candidate planning artifact only.

It does not:

- approve the PRD;
- approve a tranche;
- authorize execution;
- authorize a provider/model/tool;
- expand writable scope;
- establish root cause;
- convert inferred graph state into fact;
- close evidence gaps;
- create release authority.

Human approval remains mandatory.

## Inputs

Generation may consume only:

- current canonical application PRD;
- current application readiness/approval state;
- current governed graph projection for the same idea;
- deterministic graph scheduler output;
- exact application and graph identities.

If the PRD is absent, stale, or not current, generation is HOLD.

If graph projection/currentness fails, generation is HOLD.

If project scope differs, generation is HOLD.

## Output

The generated object must include:

- schema/version;
- idea ID;
- application identity;
- PRD content digest;
- PRD approval state;
- graph revision;
- graph projection digest;
- graph source-event hash;
- engine authority SHA;
- current graph blockers/actions;
- candidate tranche identity;
- candidate tranche objective;
- allowed surfaces;
- forbidden surfaces;
- test contract;
- stop conditions;
- external-action classification;
- routing completeness state;
- authority refs;
- generation receipt digest;
- explicit authority classification.

Authority classification is:

`CANDIDATE_PLANNING_ONLY`

## Status semantics

At minimum:

- `HOLD_PRD_REQUIRED`
- `HOLD_GRAPH_UNAVAILABLE`
- `HOLD_GRAPH_BLOCKERS`
- `HOLD_HUMAN_PRD_APPROVAL_REQUIRED`
- `READY_FOR_HUMAN_TRANCHE_REVIEW`

`READY_FOR_HUMAN_TRANCHE_REVIEW` is not execution authority.

## Determinism

Generation uses no LLM/provider call.

Same PRD content + same graph state + same application identity must produce the same candidate planning receipt.

Provider/model identity remains unchanged from Foundation 11.

## Scope guard

Generated allowed surfaces must come from governed tranche payload only.

No model or renderer may add surfaces.

No generated package may remove inherited forbidden surfaces.

At minimum, `production`, `release-authority`, and any separately frozen forbidden surfaces remain forbidden unless independently governed later.

## Human approval

Existing PRD approval remains a separate human action.

Foundation 12 does not create a new implicit approval.

Candidate tranche review must remain explicitly human before any future execution tranche can consume it.

## Definition of done

Foundation 12 is PASS only if one exact candidate proves:

1. existing human PRD behavior remains unchanged;
2. graph planning generation requires an existing current PRD;
3. current graph identity is bound into output;
4. PRD content digest is bound into output;
5. same input state yields deterministic output and receipt;
6. open graph gaps remain blockers;
7. missing PRD approval prevents ready-for-review status;
8. PRD approval alone cannot bypass graph blockers;
9. only when both approval and graph eligibility allow it may status become `READY_FOR_HUMAN_TRANCHE_REVIEW`;
10. ready-for-review is not execution authority;
11. generated tranche surfaces come only from governed graph payload;
12. forbidden surfaces cannot be removed or broadened;
13. external action classification is preserved;
14. routing/model fields are preserved but not invented;
15. no provider/model call is made by planning generation;
16. graph inference cannot become current-project fact;
17. no evidence gap is closed by generation;
18. no graph mutation is performed by read/generation;
19. stale graph/action revision fails closed;
20. cross-project graph state fails closed;
21. generation survives restart/reopen with identical identity;
22. Foundation 08 retrieval remains intact;
23. Foundation 09 convergence remains intact;
24. Foundation 10 graph-release verification remains intact;
25. Foundation 11 historical-pattern retrieval remains intact;
26. targeted tests pass;
27. full application regression passes;
28. exact-SHA app CI passes;
29. isolated Railway staging runs the exact candidate;
30. live API generation/currentness passes;
31. real browser exposes candidate planning and authority warning;
32. independent verification passes;
33. governance regression and exact-SHA governance CI pass;
34. both `main` branches and production remain untouched.

## Explicit exclusions

Foundation 12 does not authorize:

- graph-aware repair planning;
- autonomous repair execution;
- execution from candidate tranche output;
- provider/model/tool selection;
- scope expansion;
- automatic PRD approval;
- automatic tranche approval;
- cross-project learning writes;
- new generalized failure-pattern promotion;
- production promotion/deployment;
- either `main` merge.

## Stop rule

Stop at Foundation 12 acceptance boundary.

Graph-aware repair planning remains a separately governed roadmap capability after Foundation 12.
