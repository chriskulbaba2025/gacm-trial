# GACM Graph Foundation 11 â€” Historical Failure-Pattern Retrieval v1

**Status:** PASS — FOUNDATION 11 ACCEPTED
**Opened:** 2026-10-04
**Governance parent:** `e93a1f2b50feff47490dde4e99236d2a2f55b209`
**Application parent:** `85944f28dfbc3eeffce152a2ee022d52a0b4f41c`

## Purpose

Foundation 11 adds deterministic retrieval of already-governed reusable failure patterns.

It does not create new generalized knowledge.

The operating flow is:

`CURRENT PROJECT QUERY -> GOVERNED GENERALIZED PATTERN REGISTRY -> DETERMINISTIC RETRIEVAL -> ADVISORY HISTORICAL CONTEXT`

Historical patterns may improve CRIT question selection and diagnosis focus. They may not answer a current-project unknown, close an evidence gap, establish root cause, change readiness, authorize execution, approve a PRD, or satisfy release acceptance.

## Authority boundary

Only registry entries whose current governance status is exactly `GENERALIZED` are eligible for cross-project retrieval.

The runtime may not retrieve:

- PROJECT_LOCAL patterns from another project;
- CANDIDATE_GENERALIZED patterns;
- SUPERSEDED patterns;
- raw evidence from another project;
- confidential occurrence details;
- model-proposed patterns that have not passed governance;
- patterns inferred from similarity alone.

The initial authoritative registry contains only patterns that the current GACM governance repository explicitly identifies as permanent generalized failure patterns.

## Registry contract

Every retrievable pattern must contain:

- stable pattern ID;
- version;
- title;
- scope;
- signals;
- anti-signals;
- known mechanisms;
- prevention guidance;
- detecting tests/checks;
- known false positives;
- provenance references;
- currentness state;
- generalization status;
- data classification;
- cross-project-safe flag.

The registry itself is content-digested and bound to the exact governance SHA that authorized it.

Application runtime must fail closed if the vendored registry content digest or governance authority SHA does not match its manifest.

## Retrieval mechanism

Foundation 11 uses deterministic local lexical retrieval only.

No embeddings, vector database, web retrieval, external provider, model call, or paid service is authorized.

The retriever:

- filters by governance status before ranking;
- admits only `GENERALIZED`, current, cross-project-safe governance patterns;
- excludes raw occurrence evidence;
- scores current-project query terms against governed pattern fields;
- applies explicit anti-signals before returning a match;
- uses deterministic tie-breaking;
- caps result count and context size;
- emits a reproducible receipt.

## Retrieval receipt

Each retrieval receipt must preserve:

- schema/version;
- registry identity and SHA-256;
- governance authority SHA;
- query digest;
- mechanism identity;
- filter semantics;
- result IDs;
- ranking scores;
- result count;
- context size;
- authority classification;
- completeness semantics.

Completeness semantics are:

`NO_MATCH != ABSENT`

An empty result means no governed pattern was retrieved under the current deterministic mechanism. It does not prove that no relevant historical pattern exists.

## CRIT integration

CRIT may receive compact `historical_failure_pattern_context`.

Every returned pattern is:

`ADVISORY_HISTORICAL_CONTEXT_ONLY`

CRIT may use it to ask a better question or surface a verification concern.

CRIT may not treat a historical pattern as evidence about the current project.

The current project must still supply current evidence.

Pattern context must not:

- close evidence requirements;
- alter answer evidence status;
- change readiness directly;
- create graph truth;
- create convergence truth;
- expand the allowed question universe;
- mutate graph state;
- create or expand repair scope;
- authorize a provider/model/tool/action;
- approve promotion/release.

## Cross-project privacy boundary

Foundation 11 shares only generalized governance patterns.

It does not retrieve prior project records or occurrence payloads.

Registry entries must be safe for cross-project reuse and contain no client/project-specific evidence.

Any entry lacking explicit `cross_project_safe = true` is ineligible.

## Currentness

Pattern retrieval is bound to:

- registry SHA-256;
- governance authority SHA;
- application code identity.

A stale or tampered registry is HOLD.

A SUPERSEDED pattern is not retrievable.

## Definition of done

Foundation 11 is PASS only if one exact application candidate proves:

1. authoritative registry is frozen in governance;
2. application vendored registry exactly matches the governed registry digest;
3. only current GENERALIZED patterns are eligible before ranking;
4. PROJECT_LOCAL/CANDIDATE_GENERALIZED/SUPERSEDED patterns are excluded;
5. cross-project-safe filtering occurs before ranking;
6. no raw historical project evidence is present in runtime registry entries;
7. deterministic lexical retrieval is reproducible;
8. anti-signals can suppress an otherwise lexical match;
9. result count and context size are bounded;
10. retrieval receipt records registry/governance/query identities;
11. NO_MATCH remains distinct from ABSENT;
12. returned patterns are advisory historical context only;
13. CRIT can use pattern context only to improve question selection/focus;
14. pattern context cannot close current evidence gaps or readiness;
15. pattern context cannot establish root cause or causal truth;
16. pattern context cannot expand question keys;
17. pattern retrieval cannot mutate graph/current application records;
18. restart/reopen reconstructs the same registry/retrieval identity;
19. malformed/tampered/stale registry fails closed;
20. same-project Foundation 08 retrieval remains intact;
21. Foundation 09 convergence remains advisory and intact;
22. Foundation 10 graph-release verification remains intact;
23. provider/model identity remains unchanged;
24. targeted tests pass;
25. full application regression passes;
26. exact-SHA app CI passes;
27. isolated Railway staging runs the exact candidate;
28. live pattern endpoint/currentness passes;
29. real browser exposes advisory pattern context without authority inflation;
30. independent verification passes, including broader requalification if required;
31. both `main` branches and production remain untouched.

## Explicit exclusions

Foundation 11 does not authorize:

- creation or promotion of new generalized patterns;
- cross-project learning writes;
- raw cross-project evidence retrieval;
- organization-wide private history retrieval;
- PRD/tranche generation from historical patterns;
- graph-aware repair planning;
- automatic repair-scope expansion;
- causal/root-cause claims from pattern similarity;
- vector retrieval;
- embedding provider/model;
- provider/model change;
- graph mutation from historical retrieval;
- graph-triggered execution;
- production promotion/deployment;
- either `main` merge.

## Stop rule

Stop at the Foundation 11 acceptance boundary.

PRD/tranche generation from graph remains a separately governed roadmap capability after Foundation 11.

## Frozen initial registry identity

Canonical registry SHA-256: `9e0d22671581fa2086e78505e5f7032e3d28309591ac7cbe1713e1b54dea599d`.

This digest covers canonical JSON content, not platform-specific line endings.


## Acceptance result

Foundation 11 is accepted on exact application candidate:

`0f8d226b8bb28c90abf57ce5ba4f275df0d875c3`

Application parent:

`85944f28dfbc3eeffce152a2ee022d52a0b4f41c`

Governance authority freeze:

`39af22b29b77adecd0e2190c3eae4b07840f86fa`

Authoritative registry canonical SHA-256:

`9e0d22671581fa2086e78505e5f7032e3d28309591ac7cbe1713e1b54dea599d`

Accepted Railway staging deployment:

`daa1b9bf-0d42-4ccf-90a2-5a6e4e16b844`

Verification evidence:

- targeted F11 retrieval / CRIT / convergence tests: **44/44 PASS**;
- full application regression: **174/174 PASS**;
- exact-SHA application CI: **PASS**;
- candidate audit: **8 expected files, zero unexpected files, zero secret literal hits**;
- vendored registry canonical digest equals governance manifest: **PASS**;
- only current `GENERALIZED`, `GOVERNANCE_GENERALIZED`, cross-project-safe patterns are exposed: **PASS**;
- project-local, candidate-generalized, superseded and private patterns are filtered before ranking: **PASS**;
- anti-signal suppression: **PASS**;
- returned content is cryptographically bound into retrieval receipt: **PASS**;
- `NO_MATCH != ABSENT`: **PASS**;
- live matched historical-pattern retrieval: **PASS**;
- live unrelated idea `NO_MATCH`: **PASS**;
- historical context did not alter readiness or become current-project evidence: **PASS**;
- live CRIT remained `openai_api / gpt-6-luna`: **PASS**;
- live application identity equals exact candidate SHA: **PASS**;
- real Microsoft Edge acceptance: **PASS**;
- restart/reopen reconstructed identical registry and receipt identities: **PASS**;
- Foundation 08 same-project retrieval remains intact: **PASS**;
- Foundation 09 convergence remains advisory and intact: **PASS**;
- Foundation 10 graph-release verification remains intact: **PASS**;
- CL-43 remains inherited and mandatory: **PASS**;
- governance and application `main` branches remain untouched;
- production remains untouched.

Independent verifier:

`gacm-independent-verifier-v1`

Verification ID:

`verify-a7f2c324ad6545e8a63e6a9b`

Outcome: **authoritative PASS**.

Scope classification: **AUTHORITY_BEARING**. Broader requalification was required and completed by the targeted/full-regression/CI/live/browser/restart evidence above.

### Acceptance decision

All Foundation 11 definition-of-done items are satisfied.

Foundation 11 closes **PASS** at the isolated staging-candidate boundary.

Graph-derived PRD/tranche generation is the next roadmap capability. It is not opened by this acceptance.
