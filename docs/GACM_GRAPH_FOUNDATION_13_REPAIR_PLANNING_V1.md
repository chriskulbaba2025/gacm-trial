# GACM Graph Foundation 13 — Graph-Aware Repair Planning and Graph Integrity Preconditions v1

**Status:** FROZEN IMPLEMENTATION CONTRACT
**Effective:** 2026-10-04
**Governance parent:** `6df6e99e3cf896862f220d9f1320866a569a87ea`
**Application parent:** `f20cf367e8611025ffa1cb5e698db37350537c2c`
**Roadmap authority:** `docs/GACM_FOUNDATION_COMPLETION_ROADMAP_V1.md`
**Boundary:** isolated candidate/staging only; production and both `main` branches are excluded.

## 1. Objective

Foundation 13 converts a verified current FAIL/HOLD that requires repair into a bounded, evidence-linked **candidate repair tranche** without executing the repair.

The canonical flow is:

`VERIFICATION FAILURE + CURRENT GRAPH + CURRENT EVIDENCE + CURRENT PLANNING + HISTORICAL GENERALIZED PATTERNS -> GOVERNED REPAIR PROJECTION -> CANDIDATE REPAIR TRANCHE`

Foundation 13 must also close graph-integrity gaps that become material once graph reasoning is allowed to influence repair scope.

## 2. Authority and non-authority

Current application records, exact application identity, current graph identity, current PRD/planning identity, the independent verification receipt and accepted governance contracts remain authoritative inputs.

Convergence output and historical failure-pattern retrieval are advisory. They may prioritize diagnosis but cannot establish root cause, close an evidence gap, expand scope, create product truth, create execution authority or approve a repair.

A retrieval result of `NO_MATCH` means only that no eligible pattern was returned. It never means the failure class is absent.

Foundation 13 output authority is:

`CANDIDATE_REPAIR_PLANNING_ONLY`

Every output must preserve:

`execution_authorized = false`

## 3. Required verification receipt

A repair plan may be generated only from a durable current verification receipt that proves:

- exact idea/project identity;
- exact application candidate/planning binding identity;
- independent verifier identity and `INDEPENDENT_VERIFIER` issuer role;
- a non-PASS verifier outcome of `FAIL`, `BLOCKED`, or `UNOBSERVABLE`, mapped to repair `FAIL/HOLD` semantics;
- preservation of the existing verifier authority invariant: only independent `PASS` may carry `authoritative = true`; a repair-triggering non-PASS receipt must carry `authoritative = false`;
- failed work-unit/tranche identity;
- failed/affected surfaces;
- defect-family identity;
- diagnosis status;
- root-cause statement and owning boundary when diagnosis is evidenced;
- evidence references supporting the diagnosis;
- repair-attempt history;
- prior assurance classifications potentially affected.

Missing, stale, malformed, self-certified or cross-project verification input is HOLD.

## 3A. Existing verifier and repair-scope authority

Foundation 13 must compose the already accepted GACM controls rather than create parallel replacements.

The existing `gacm-independent-verifier-v1` remains the issuer of verification decisions. Foundation 13 validates its non-PASS receipt identity and preserves its semantics; it does not redefine a failed verification as an authoritative PASS-equivalent receipt.

The existing `gacm.repair.RepairScopePlanner` remains the deterministic repair-scope / dependency engine. Foundation 13 may bind graph currentness, diagnosis, convergence and historical-pattern context around its result, but may not duplicate or override its scope classification, assurance invalidation or requalification decisions.

Because Foundation 14 has not yet created the trusted candidate-tranche execution bridge, Foundation 13 repair planning is an **internal governed component boundary**. It must not expose an unauthenticated/untrusted public HTTP endpoint that accepts caller-authored verification receipts. Foundation 14 will own durable trusted binding from execution/verification state into this component.

## 4. Repair-scope rules

The planner must:

- identify root cause, owning boundary, related failure modes and blast radius;
- remain inside the current candidate tranche's allowed surfaces;
- preserve all inherited forbidden surfaces;
- reject any failed surface that is forbidden or outside the current allowed scope;
- calculate the smallest bounded repair surface supported by the verification receipt;
- record the current defect-family repair-attempt count;
- identify prior assurances that require reverification or broader requalification;
- preserve provider/model/tool restrictions and external-action classification;
- preserve rollback/irreversibility semantics;
- preserve the frozen product definition of done;
- produce a candidate repair tranche only.

If the receipt does not contain an evidenced diagnosis sufficient to choose an owning boundary, status must be `HOLD_DIAGNOSIS_REQUIRED`; the planner may expose advisory convergence/pattern context but may not invent the diagnosis.

## 5. Repair-attempt control

Repair history is durable, ordered and identity-bound.

For the same defect family:

- attempts 0–2 may produce a candidate repair tranche when all other gates pass;
- three failed repair attempts require `RESET_DIAGNOSIS_REQUIRED`;
- duplicate attempt IDs, malformed history, stale candidate identity or non-monotonic attempt numbers fail closed;
- the planner cannot erase failed approaches by omitting them from the current authoritative receipt.

## 6. Graph-integrity preconditions

Before graph-derived information may affect repair scope, Foundation 13 must enforce:

### Canonical identity

Durable graph object IDs must be unique within the project. Alias/duplicate-candidate information may be advisory, but no model or planner may silently merge or split durable identities.

### Conflict mechanics

Material unresolved conflict must be represented explicitly and must block a repair-scope conclusion when the conflict affects the proposed owning boundary, failed surface, evidence or authority.

Copied, summarized, mirrored or otherwise dependent evidence must not be silently counted as independent corroboration.

### Epistemic path composition

A chain containing `UNKNOWN`, `HYPOTHESIS`, `INFERRED`, stale, conflicted or unauthorized material cannot yield a stronger authoritative conclusion than its weakest material link.

Convergence remains candidate inference and never becomes root-cause truth by composition.

### Operational/graph consistency

The current application/operational state and current graph projection must bind to the same project/current event identity. Material split-brain is HOLD.

### Retrieval negative semantics

`NO_MATCH != ABSENT`.

Failure to retrieve a historical pattern or bounded graph item cannot close a gap or prove non-existence.

### Mutation impact

Repair planning is read-only. It performs no graph mutation. Any future mutation proposed by the repair must remain a future execution concern and may not be accepted by this planner.

### Reasoning provenance

The receipt must bind the deterministic planner identity and the exact identities/digests of material current inputs. If model-assisted or retrieved advisory context is included, its provider/model/retrieval receipt identities must be preserved without storing private chain-of-thought.

### Independent challenge

Any graph assertion or repair-scope claim used to satisfy a later execution/release gate must remain independently verifiable from durable evidence.

## 7. Candidate repair tranche

When ready, output must include at least:

- repair work-unit ID;
- target object/tranche identity;
- defect-family ID;
- root-cause statement;
- owning boundary;
- bounded repair surfaces;
- inherited allowed surfaces;
- inherited forbidden surfaces;
- affected dependencies/blast radius;
- invalidated assurance classes;
- targeted test contract;
- required broader requalification;
- stop conditions;
- repair-attempt number;
- rollback/irreversibility classification;
- external-action/provider/model restrictions;
- verification/evidence identity;
- graph/planning/convergence/failure-pattern receipt identities;
- candidate repair-planning digest;
- `human_repair_review_required = true`;
- `execution_recipe_created = false`;
- `execution_authorized = false`.

## 8. Determinism and currentness

For identical authoritative inputs, repair planning must produce an identical receipt/digest.

Planning is read-only with respect to application, graph and governance state.

Stale graph revision, stale projection digest, stale source event, stale application SHA, stale planning receipt, stale verification receipt or cross-project identity must fail closed.

## 9. Explicit exclusions

Foundation 13 does not authorize:

- repair execution;
- execution-recipe creation;
- automatic repair approval;
- automatic root-cause acceptance;
- scope expansion;
- provider/model/tool selection;
- model escalation;
- subagents/parallel child runs;
- automatic cross-project learning writes;
- generalized failure-pattern promotion;
- production mutation or promotion;
- either `main` merge;
- Foundation 14 execution work;
- an untrusted public/network repair-planning input surface.

## 10. Acceptance contract

Foundation 13 may close PASS only when the exact application candidate proves:

1. deterministic positive candidate repair planning from a current independently verified failure;
2. `execution_authorized = false` in every result;
3. missing/non-independent verification fails closed;
4. stale verification/application/planning/graph identity fails closed;
5. cross-project identity fails closed;
6. diagnosis missing/unsupported returns `HOLD_DIAGNOSIS_REQUIRED`;
7. unsupported causal certainty from convergence is rejected;
8. historical patterns remain advisory and `NO_MATCH` is not absence;
9. unresolved material graph conflict blocks affected repair planning;
10. duplicate/colliding graph object identity fails closed;
11. failed surfaces outside allowed scope or inside forbidden surfaces fail closed;
12. inherited `production` and `release-authority` restrictions remain present;
13. repair attempt 0–2 can be planned and attempt 3 requires `RESET_DIAGNOSIS_REQUIRED`;
14. invalidated assurance classes and broader-requalification requirement are deterministic;
15. restart/reopen reproduces the same repair-planning identity;
16. planning performs no graph mutation;
17. Foundation 08 retrieval, Foundation 09 convergence, Foundation 10 graph-release verification, Foundation 11 failure-pattern retrieval and Foundation 12 PRD/tranche planning remain intact;
18. targeted tests pass;
19. full application regression passes;
20. compile/diff/secret/scope checks pass;
21. exact-SHA application CI passes;
22. isolated staging currentness/live API proof passes if deployed for acceptance;
23. independent verification passes;
24. governance regression and exact-SHA governance CI pass;
25. production and both `main` branches remain untouched.

## 11. Stop rule

Stop at Foundation 13 acceptance boundary.

Foundation 14 — Governed Candidate-Tranche Execution Bridge — remains planned but not opened by Foundation 13 acceptance.

## 12. Acceptance result

Foundation 13 is accepted on exact application candidate:

`df2ede96481f13905fe1dc9459a096cbebe329cc`

Application parent:

`f20cf367e8611025ffa1cb5e698db37350537c2c`

Governance authority before this acceptance record:

`84957631bccbc0c917a359ea2a5451e21082562f`

Verification evidence:

- Foundation 13 direct repair-planning tests: **19/19 PASS**;
- Foundation 08-13 targeted retrieval/convergence/failure-pattern/planning/repair regression: **58/58 PASS**;
- full application regression: **202 tests + 28 subtests PASS**;
- compileall: **PASS**;
- `git diff --check`: **PASS**;
- changed-path scope check: **PASS** - exactly `app.py`, `graph_runtime.py`, `repair_planning.py`, `tests/test_repair_planning.py`;
- staged secret scan: **PASS**;
- untrusted public repair-planning endpoint absent: **PASS**;
- exact-SHA application CI: **PASS**, run `37233740601`, job `111528636745`, exact SHA `df2ede96481f13905fe1dc9459a096cbebe329cc`;
- deterministic candidate repair planning from an existing independent non-PASS verifier receipt: **PASS**;
- accepted `RepairScopePlanner` remains repair-scope authority: **PASS**;
- repair output remains `CANDIDATE_REPAIR_PLANNING_ONLY` and `execution_authorized = false`: **PASS**;
- inferred/unsupported diagnosis remains HOLD: **PASS**;
- three failed attempts require diagnosis reset: **PASS**;
- stale application/planning/project binding fails closed: **PASS**;
- forbidden/out-of-scope repair surfaces fail closed: **PASS**;
- convergence cannot create causal truth: **PASS**;
- historical `NO_MATCH` cannot become absence: **PASS**;
- unresolved graph conflict and identity-resolution requirements fail closed: **PASS**;
- graph repair context is read-only and performs no graph mutation: **PASS**;
- restart/reopen reproduces the same repair-planning identity: **PASS**;
- independent verification `verify-43b43a36f351086146238c5b`: **authoritative PASS**;
- independent scope classification: **ARCHITECTURE_BEARING**;
- broader requalification required: **true** and completed through the 58-test targeted suite, complete application regression, static gates and exact-SHA CI;
- hosted staging/browser proof for this new Foundation 13 component: **NOT_APPLICABLE** because the frozen contract deliberately prohibits a public/untrusted repair-planning input surface; no deployment was required to prove the internal component;
- production remains untouched;
- application and governance `main` remain untouched.

### Acceptance decision

Foundation 13 is **PASS** at the isolated candidate boundary. Final governance regression passed 274/274 and exact-SHA governance CI passed on acceptance SHA `9e9dc75036711bf144cc6a91fa8e7f0eec713163` (run `37234072910`, job `111529600899`).

The mandatory stop rule applies: Foundation 14 and every later stage remain **not opened**.
