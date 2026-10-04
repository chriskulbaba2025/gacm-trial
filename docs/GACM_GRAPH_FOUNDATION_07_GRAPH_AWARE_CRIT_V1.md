# GACM Graph Foundation 07 — Graph-Aware CRIT v1

**Status:** AUTHORIZED IMPLEMENTATION BOUNDARY
**Opened:** 2026-10-03
**Governance parent:** `c50ba6e5f5382b3460f0ab1de7d508f330ced800`
**Application parent:** `32d474fdb8fe0672d826ff434b4bfc94c9537407`

## Purpose

Foundation 07 makes CRIT question selection aware of the already-governed per-idea graph without transferring authority to the model and without adding retrieval, convergence, autonomous execution, or production scope.

The graph remains a governed control projection. SQLite remains authoritative application state. The model remains a bounded semantic reviewer.

## Exact scope

Foundation 07 may add only:

- a bounded graph-to-CRIT context projection;
- exact graph-currentness identity on that projection;
- CRIT selection/review access to that bounded projection;
- durable provenance linking generated questions and answers to the graph context identity used;
- fail-closed behavior when required graph context is unavailable, malformed, cross-project, or stale;
- tests and browser/API observability needed to prove the above.

## Graph context allowed into CRIT

The bounded context may contain only governed fields needed to prioritize material unknowns:

- idea/project identity;
- graph revision;
- graph projection digest;
- source event hash;
- governed engine authority SHA;
- active open evidence-gap IDs and their existing governed requirement text / claim IDs;
- deterministic scheduler next-action kind, target, reason, and blocker IDs;
- an explicit authority label stating that this is context only.

It must not copy the complete graph, mutation history, secrets, provider credentials, raw unrelated records, or cross-project state.

## Authority rule

Graph context is:

`ADVISORY_GOVERNED_CONTEXT_ONLY`

It may help CRIT prioritize, word, or stop an already-authorized question.

It may not:

- invent a new question dimension or candidate key;
- turn UNKNOWN / PARTIAL / UNVERIFIED into fact;
- mark evidence verified;
- close an evidence gap;
- alter graph state or graph revision;
- change readiness;
- approve a PRD;
- select a provider or model;
- route execution;
- create a work unit;
- promote, release, or roll back;
- create retrieval or convergence output.

The authorized question universe remains `PRODUCT_QUESTIONS`. CRIT may choose only a key already present in the supplied candidate set.

## Currentness and fail-closed behavior

Before graph context reaches CRIT:

1. the vendored graph engine identity must verify;
2. the graph must reconstruct and validate for the same idea;
3. the graph projection must be synchronized from the current committed application record;
4. the returned context must name the same idea;
5. graph revision, projection digest, source event hash, and engine authority identity must be structurally valid.

If any check fails, graph-aware question selection does not fall back to graph-blind selection.

The human interview remains readable, but new CRIT selection is `REVIEW_UNAVAILABLE` until governed graph context is current again.

A human answer already submitted must never be discarded because graph context or CRIT review is unavailable. Existing fail-closed answer-review semantics remain in force.

## Provenance

Every CRIT-selected question must persist a compact `graph_context_identity` containing:

- graph revision;
- projection digest;
- source event hash;
- engine authority SHA.

Every saved answer must preserve the graph-context identity of the question that was answered.

A CRIT-generated follow-up may use the same bounded graph context and must preserve its identity. The graph identity is provenance only; it does not make the generated wording authoritative.

## Provider/model boundary

Foundation 07 does not change provider or model authority.

Hosted staging remains:

- provider: OpenAI API direct;
- model: `gpt-6-luna`;
- no fallback;
- no model escalation;
- no external tools;
- no web/retrieval calls;
- `store=false`;
- credentials remain Railway secrets and are never committed.

## Definition of done

Foundation 07 is PASS only if all are proven on one exact application candidate:

1. bounded graph context projection is deterministic and project-isolated;
2. projection contains no complete graph dump, mutation history, secret, or raw unrelated project data;
3. CRIT receives graph context during initial/next question selection;
4. CRIT may select only an existing authorized candidate key;
5. selected question persists exact graph-context identity;
6. saved answer preserves the identity of the question it answered;
7. CRIT follow-up review can receive the bounded graph context without granting it authority;
8. missing/tampered/cross-project graph context fails closed without graph-blind fallback;
9. submitted human answers remain durable if semantic/graph review becomes unavailable;
10. strong, mixed, and weak fresh-input behavior remains correct;
11. graph runtime/persistence/reopen invariants remain correct;
12. full application regression passes;
13. exact-SHA CI passes;
14. isolated Railway staging runs the exact candidate;
15. live CRIT question provenance proves the graph identity used;
16. real browser acceptance passes;
17. independent verification passes;
18. production remains untouched.

## Explicit exclusions

Foundation 07 does not authorize:

- lexical or vector retrieval;
- embeddings;
- convergence/shared-root detection;
- graph-triggered execution;
- legacy-planner removal;
- cross-project learning;
- autonomous learning or rule promotion;
- provider/model changes;
- application production deployment;
- production promotion.

## Stop rule

Stop at the Foundation 07 acceptance boundary. Bounded retrieval is the next roadmap item only after Foundation 07 independently passes.
