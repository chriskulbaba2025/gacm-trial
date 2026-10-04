# GACM Graph Foundation 09 — Convergence / Shared-Root Detection v1

**Status:** PASS — ACCEPTED STAGING CANDIDATE / STOP AT FOUNDATION 09 BOUNDARY
**Opened:** 2026-10-04
**Governance parent:** `40ec4c4a063f6e03e1e182a9627b7ceec880942c`
**Application parent:** `c2b4f89d918dcf8c73bde8a490f6f42535f94038`

## Purpose

Foundation 09 adds deterministic same-project convergence detection over already-governed qualification artifacts and current graph identity.

The detector may emit only:

`POSSIBLE_SHARED_ROOT_CAUSE`

It does not establish `CAUSED_BY`, `ROOT_CAUSE`, or any equivalent causal truth.

## Authorized signals

A convergence candidate may be emitted only when at least one of these deterministic signals exists:

1. an explicit current `converges_with` relationship between two eligible findings; or
2. two eligible findings share at least two exact evidence-requirement IDs.

Eligible findings are current same-project risks, dependencies, qualification criteria, adversarial findings, claims, assumptions, and guardrails already present in the authoritative application artifacts.

Lexical similarity, shared vocabulary, graph proximity, common object type, vector similarity, model judgment, or co-occurrence alone are insufficient.

## Output authority

Every candidate must contain:

- stable candidate ID;
- exact member object IDs;
- signal type;
- exact shared evidence IDs and/or relationship ID;
- human-readable deterministic reason;
- current artifact snapshot identities;
- current graph revision/projection digest/source-event hash;
- `epistemic_state = POSSIBLE_SHARED_ROOT_CAUSE`;
- `authority = ADVISORY_DIAGNOSTIC_ONLY`;
- `diagnosis_required = true`.

A candidate cannot:

- close evidence gaps;
- mark a root cause proven;
- mutate graph state;
- enlarge repair scope automatically;
- create a work unit;
- route a model/provider;
- approve a PRD;
- change readiness;
- trigger execution;
- block or promote a release by itself.

Where downstream repair/release logic later consumes this signal, the separate governed consumer must enforce the required diagnosis.

## Scope and currentness

The detector is scoped to exactly one current `idea_id`.

It must fail closed on:

- cross-project object IDs;
- malformed artifact identities;
- stale graph identity;
- missing required provenance;
- unsupported relationship types;
- duplicate/colliding candidate identities;
- non-deterministic ordering.

The detector must be reproducible from the same SQLite artifact state plus the same current graph identity.

## Positive and negative controls

Acceptance must prove both error classes:

- true-positive: explicit `converges_with` and exact multi-evidence-lineage cases are detected;
- false-positive: materially different findings sharing only vocabulary, one evidence ID, or object type are rejected.

No lexical or model-based heuristic may be used to make convergence decisions.

## Provider/model boundary

The convergence detector has no provider, model, credential, network access, embedding call, or external index.

Foundation 09 does not modify hosted CRIT authority:

- provider: OpenAI API direct;
- model: `gpt-6-luna`;
- no fallback;
- no escalation;
- no tool authority;
- `store=false`.

The convergence output is not supplied to CRIT in Foundation 09.

## Definition of done

Foundation 09 is PASS only if one exact candidate proves:

1. same-project filtering occurs before detection;
2. explicit `converges_with` produces a candidate;
3. >=2 exact shared evidence requirement IDs produce a candidate;
4. one shared evidence ID alone does not;
5. shared vocabulary alone does not;
6. graph proximity alone does not;
7. candidates are stably ordered and reproducible;
8. each candidate records the exact reason and provenance;
9. candidates remain `POSSIBLE_SHARED_ROOT_CAUSE` / advisory only;
10. detector cannot mutate graph or application state;
11. detector cannot alter readiness/question universe/PRD authority;
12. current graph identity is bound into the result;
13. stale/malformed/cross-project inputs fail closed;
14. process reopen reconstructs the same candidate set from durable state;
15. live staging returns the exact detector output/currentness identity;
16. real browser audit visibly exposes candidate reasons and advisory authority;
17. targeted positive/negative controls pass;
18. full application regression passes;
19. exact-SHA CI passes;
20. independent verification passes, including broader requalification if required;
21. CRIT remains `openai_api / gpt-6-luna`;
22. both `main` branches and production remain untouched.

## Explicit exclusions

Foundation 09 does not authorize:

- authoritative causal claims;
- model-based convergence;
- vector-based convergence;
- cross-project convergence or learning;
- generalized failure-pattern promotion;
- automatic repair-scope expansion;
- graph mutation from convergence;
- graph-triggered execution;
- legacy planner removal;
- provider/model changes;
- production deployment/promotion;
- either `main` merge.

## Stop rule

Stop at the Foundation 09 acceptance boundary.

Independently verified graph-derived release acceptance remains the next roadmap capability after Foundation 09 independently passes.

## Acceptance result

Foundation 09 is accepted on exact application candidate:

`85944f28dfbc3eeffce152a2ee022d52a0b4f41c`

with Foundation 08 application parent:

`c2b4f89d918dcf8c73bde8a490f6f42535f94038`

The candidate is preserved on remote branch `candidate/foundation09-convergence-20261004`. Qualification-app `main` remains unchanged at `32d474fdb8fe0672d826ff434b4bfc94c9537407`.

Accepted Railway staging deployment:

`7bf642a9-ff27-4efa-9570-6c8d6adb5f1e`

### Accepted detector

Detector identity:

`gacm-deterministic-convergence-v1`

The detector is same-project, deterministic and read-only. It emits only `POSSIBLE_SHARED_ROOT_CAUSE` using:

- an explicit current `converges_with` relationship; or
- at least two exact shared evidence-requirement IDs.

It does not use lexical similarity, vector similarity, model judgment, or graph proximity as convergence authority. It performs no graph mutation and does not establish authoritative root cause.

### Verification evidence

- targeted convergence/runtime/browser tests: **58/58 PASS**;
- full application regression: **163/163 PASS**;
- exact-SHA application CI: **PASS** on `85944f2...`;
- candidate audit: four expected files only, zero unexpected files;
- initial secret-scan hit was diagnosed as a false positive from the substring `sk-` inside ordinary `risk-*` identifiers; corrected realistic secret scan: zero hits;
- live Railway convergence API: **PASS**;
- live detector returned five current same-project candidates;
- explicit `converges_with` pair `v1-risk-003 | v1-risk-006`: **detected**;
- exact multi-evidence-lineage pair `v1-adv-007 | v1-dep-003`: **detected**;
- superficial vocabulary / one-evidence overlap negative control: **rejected**;
- graph-proximity-only negative control: **rejected**;
- process reopen reconstructed the identical result digest and candidate set;
- graph bytes remained unchanged by detection;
- live result reconciles to current graph revision/projection/source-event identity;
- real Microsoft Edge browser acceptance: **PASS**, visibly showing advisory authority, `POSSIBLE_SHARED_ROOT_CAUSE`, detector identity, exact result digest, diagnosis requirement, and explicit causal limit;
- local SHA == remote candidate SHA == Railway commit == served runtime SHA;
- canonical local source-tree SHA-256 == served SHA-256: `ca63407502d8f36bf43772206a0b0a0e375c9ee50e4a1ae5c59bba46b45b5d3a`;
- hosted CRIT remained `openai_api / gpt-6-luna`;
- production mutation: **NONE**.

### Independent verification

GACM verifier `gacm-independent-verifier-v1` issued authoritative **PASS**:

`verify-cf8f3cf56c6041bfeb5465ea`

The exact delta is correctly classified `ARCHITECTURE_BEARING`. Broader requalification was required and completed using the 163/163 full regression, 58/58 targeted suite, positive and false-positive convergence controls, process-reopen reconstruction, live Railway currentness/API proof, and real Edge acceptance.

### Acceptance decision

All 22 Foundation 09 definition-of-done items are satisfied.

Foundation 09 therefore closes **PASS** at the accepted staging-candidate boundary.

Independently verified graph-derived release acceptance remains the next roadmap capability. It is not opened by this acceptance.
