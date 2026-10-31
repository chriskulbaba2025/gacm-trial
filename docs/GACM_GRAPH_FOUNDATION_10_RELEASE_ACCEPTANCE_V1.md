# GACM Graph Foundation 10 â€” Independently Verified Graph-Derived Release Acceptance v1

**Status:** PASS — ACCEPTED GOVERNANCE CANDIDATE / STOP AT FOUNDATION 10 BOUNDARY
**Opened:** 2026-10-04
**Governance parent:** `4bd875e268fa2700e5aa945711ebe65213adc587`
**Accepted application staging candidate under proof:** `85944f28dfbc3eeffce152a2ee022d52a0b4f41c`

## Purpose

Foundation 10 closes the release-acceptance blind spot for graph-backed GACM reasoning.

The graph may contribute materially to a release decision, but the graph is not release authority.

The independent verification layer must independently validate the exact graph-derived evidence and release-currentness identities that contributed to the release decision.

The governing flow is:

`GRAPH-BACKED RELEASE EVIDENCE -> INDEPENDENT GRAPH RELEASE CHECK -> AUTHORITATIVE VERIFICATION RECEIPT -> PROMOTION ELIGIBILITY`

The promotion/release layer may consume the verifier result. It may not trust executor-authored or graph-authored claims of release PASS.

## CL-43 inheritance

Foundation 10 inherits `CL-43 â€” EXECUTION AUTHORITY AND INFERENCE STATE` without weakening it.

Any execution-ready work unit used to produce release evidence still requires:

- a frozen execution recipe;
- exact recipe digest;
- explicit execution-authority state;
- deterministic per-action `ALLOW / DENY`;
- bounded judgment only in declared slots;
- governed re-freeze for recipe mutation.

Foundation 10 does not create an alternate execution path.

## Graph release evidence contract

Graph-backed release evidence is required when the work-unit contract declares:

`graph_release_required = true`

The raw evidence must bind the exact candidate and reasoning state.

Required top-level identities:

- project ID;
- candidate SHA;
- candidate artifact identity;
- remote candidate SHA;
- deployed artifact SHA;
- served runtime SHA;
- environment identity;
- build/deployment identity;
- graph schema identity;
- graph revision;
- graph projection digest;
- graph source-event hash;
- graph engine authority SHA;
- graph engine manifest digest;
- source-tree/runtime identity where available.

Release currentness requires:

`candidate SHA = remote candidate SHA = deployed artifact SHA = served runtime SHA`

Any mismatch is FAIL.

## Graph currentness

Graph-derived evidence used for release must match the exact current graph identity named by the release evidence:

- graph revision;
- projection digest;
- source-event hash;
- engine authority SHA.

A graph-backed artifact stamped with an older graph revision/digest is stale.

Stale graph-derived evidence cannot satisfy release acceptance.

No model, memory, prior chat, or older receipt may substitute for current graph evidence.

## Retrieval provenance

If bounded retrieval contributed materially to a release-relevant assertion, release evidence must identify:

- retrieval mechanism;
- lexical/index identity;
- receipt digest;
- graph revision;
- graph projection digest;
- corpus snapshot digest;
- query digest;
- returned object IDs.

The retrieval graph revision and projection digest must match the release graph identity.

A stale retrieval receipt is FAIL when marked materially used.

Retrieval remains advisory context. It does not become proof or release authority.

## Convergence provenance

If convergence/shared-root detection contributed materially to the release review, release evidence must identify:

- detector identity;
- result digest;
- graph revision;
- projection digest;
- source-event hash;
- candidate count;
- epistemic limit;
- authority classification;
- authoritative-root-cause flag.

The verifier must reject convergence evidence if:

- graph identity is stale;
- authority is not `ADVISORY_DIAGNOSTIC_ONLY`;
- epistemic limit is not `POSSIBLE_SHARED_ROOT_CAUSE`;
- authoritative root cause is claimed;
- lexical/vector/model judgment is represented as causal authority.

A convergence candidate cannot by itself satisfy a release gate.

## Release assertions

Every graph-derived assertion claimed to satisfy a release gate must include:

- assertion ID;
- assertion kind;
- exact object IDs;
- exact evidence IDs;
- provenance references;
- graph revision;
- projection digest;
- epistemic state;
- verification state;
- release-gate role.

Only assertions with:

- `epistemic_state in {EVIDENCED, ACCEPTED}`;
- `verification_state = VERIFIED`;
- non-empty evidence IDs;
- non-empty provenance;
- current graph revision/digest;

may satisfy a release gate.

The following states may never independently satisfy a release gate:

- USER_STATED;
- OBSERVED;
- INFERRED;
- HYPOTHESIS;
- CONFLICTED;
- UNKNOWN;
- SUPERSEDED;
- POSSIBLE_SHARED_ROOT_CAUSE.

They may remain visible as context or limits.

## Independent verifier authority

The independent verification engine must recompute the graph-release result from the raw evidence.

It must not accept a claimed graph-release PASS from:

- executor;
- graph;
- CRIT;
- retrieval subsystem;
- convergence detector;
- orchestrator;
- promotion layer.

The verification receipt must carry:

- `graph_release_result`;
- `graph_release_evidence_digest`.

For graph-backed release acceptance, authoritative PASS requires:

`graph_release_result = PASS`

Only the independent verifier may issue that PASS.

## Promotion eligibility

When `graph_release_required = true`, promotion eligibility must require an authoritative independent verification receipt whose:

- overall status is PASS;
- issuer role is `INDEPENDENT_VERIFIER`;
- authoritative flag is true;
- graph release result is PASS;
- graph release evidence digest exactly matches the release evidence being promoted.

A generic independent-verifier PASS without graph-release verification is insufficient.

Foundation 10 does not authorize promotion itself.

## Failure states

Foundation 10 must fail closed on at least:

- missing graph release evidence;
- malformed graph identity;
- project mismatch;
- candidate/remote/deployed/served SHA mismatch;
- graph revision mismatch;
- projection digest mismatch;
- source-event mismatch;
- engine authority mismatch;
- stale materially-used retrieval receipt;
- stale convergence result;
- convergence promoted to causal truth;
- graph assertion without evidence/provenance;
- graph assertion in non-qualifying epistemic state;
- graph assertion not independently VERIFIED;
- graph assertion stamped to stale graph identity;
- claimed graph release PASS without independent recomputation;
- promotion evidence digest mismatch.

## Availability

For graph-backed release acceptance:

`GRAPH AVAILABILITY = REQUIRED`

If graph release evidence is unavailable or cannot be independently verified:

`RELEASE ACCEPTANCE = BLOCKED / UNOBSERVABLE`

There is no silent fallback to model memory or prior receipts.

## Definition of done

Foundation 10 is PASS only if one exact governance candidate proves:

1. graph release checking is part of independent verification, not executor or graph authority;
2. non-graph verification remains backward compatible;
3. graph-backed verification requires raw graph release evidence;
4. exact candidate/remote/deployed/served identity is enforced;
5. exact graph revision/projection/source-event/engine identity is enforced;
6. stale materially-used retrieval evidence fails;
7. stale convergence evidence fails;
8. `POSSIBLE_SHARED_ROOT_CAUSE` cannot satisfy a release gate;
9. unsupported epistemic states cannot satisfy release gates;
10. EVIDENCED/ACCEPTED + VERIFIED + provenance/evidence can satisfy a release gate;
11. graph release evidence digest is deterministic;
12. verification receipt records graph release result/digest;
13. run-state projection preserves graph-release verification result/digest;
14. promotion eligibility requires matching graph-release verifier PASS when graph release is required;
15. generic verifier PASS without graph-release result is rejected for graph-backed promotion;
16. executor/graph claimed PASS cannot override independent result;
17. stale graph-derived artifact negative control is proven against live staging evidence;
18. a current exact live staging evidence package can independently PASS;
19. existing promotion/generalization/provider gates remain intact;
20. targeted verification/promotion tests pass;
21. full GACM governance regression passes;
22. exact-SHA CI passes;
23. independent verification of the Foundation 10 implementation passes;
24. GACM `main`, qualification-app `main`, Railway source/deployment, and production remain unchanged;
25. no production promotion or `main` merge occurs.

## Explicit exclusions

Foundation 10 does not authorize:

- graph-owned release authority;
- promotion of the Foundation 09 staging candidate;
- production deployment;
- either `main` merge;
- graph-triggered promotion;
- autonomous release;
- causal promotion of convergence candidates;
- vector/model convergence;
- cross-project learning;
- provider/model changes;
- qualification-app code changes;
- Railway configuration changes.

## Stop rule

Stop at the Foundation 10 acceptance boundary.

Any subsequent promotion or production work requires a separate governed objective and explicit release authority.

## Acceptance result

Foundation 10 is accepted on exact governance implementation candidate:

`5dcaa68227169e0db7c857251748205ac7e1e5d1`

with frozen authority parent:

`d9ce4aad78dce554c110552afd989be7ad525981`

The live application evidence target remained the unchanged Foundation 09 Railway staging deployment:

- application SHA: `85944f28dfbc3eeffce152a2ee022d52a0b4f41c`;
- deployment: `7bf642a9-ff27-4efa-9570-6c8d6adb5f1e`;
- source-tree SHA-256: `ca63407502d8f36bf43772206a0b0a0e375c9ee50e4a1ae5c59bba46b45b5d3a`.

No application or Railway mutation was required.

### Verification evidence

- targeted graph-release / independent-verification / promotion / schema suite: **60/60 PASS**;
- full GACM governance regression: **274/274 PASS**;
- authority-freeze CI on `d9ce4aa...`: **PASS**;
- exact implementation CI on `5dcaa68...`: **PASS**;
- implementation candidate audit: nine expected files only, zero unexpected files, zero secret literal hits;
- non-graph independent verification remains backward compatible: **PASS**;
- graph-backed verification without raw graph evidence becomes UNOBSERVABLE: **PASS**;
- exact candidate = remote candidate = deployed artifact = served runtime enforcement: **PASS**;
- exact graph schema/revision/projection/source-event/engine/manifest binding: **PASS**;
- qualifying EVIDENCED/ACCEPTED + VERIFIED assertion rule: **PASS**;
- non-qualifying epistemic-state negative controls: **PASS**;
- convergence remains `POSSIBLE_SHARED_ROOT_CAUSE / ADVISORY_DIAGNOSTIC_ONLY`: **PASS**;
- promotion eligibility requires matching independent graph-release PASS/digest/verification-receipt binding: **PASS**;
- promotion receipt preserves graph-release evidence digest and verification ID: **PASS**;
- promotion itself was **not executed**.

### Live staging proof

Current live graph release evidence independently evaluates:

`PASS`

with evidence digest:

`ff06d747878542687aa9f39fb9c5c883751b4d44806b9c1a4fd6911f28fc21a5`

Live current graph revision:

`4`

A persisted CRIT/retrieval receipt from graph revision:

`3`

was deliberately evaluated as materially release-relevant and correctly returned:

`FAIL — material retrieval evidence is stale relative to release graph`

This proves the gate rejects stale graph-derived release context rather than relying on prior acceptance or conversation memory.

### Independent verification

GACM verifier `gacm-independent-verifier-v1` issued authoritative **PASS**:

`verify-2404d6cc5f582031022df0f8`

The verification receipt itself records:

- `graph_release_result = PASS`;
- exact live graph-release evidence digest `ff06d747878542687aa9f39fb9c5c883751b4d44806b9c1a4fd6911f28fc21a5`.

The Foundation 10 implementation is correctly classified:

`AUTHORITY_BEARING`

Broader requalification was required and completed using the 60/60 targeted suite, 274/274 full governance regression, exact-SHA CI, live current graph-release PASS, live stale-retrieval FAIL negative control, promotion-binding tests, and preserved CL-43 controls.

### Acceptance decision

All 25 Foundation 10 definition-of-done items are satisfied.

Foundation 10 therefore closes **PASS** at the governance-candidate boundary.

This acceptance does not promote the application, mutate Railway, merge either `main`, or touch production.

Any subsequent promotion/release/SETTLE or reusable-learning work requires a separate governed objective.
