# GACM Graph Foundation 08 â€” Bounded Retrieval v1

**Status:** PASS — ACCEPTED STAGING CANDIDATE / STOP AT FOUNDATION 08 BOUNDARY
**Opened:** 2026-10-04
**Governance parent:** `fe88539e82ac89f675ef4111a687f2bdbcffcb39`
**Application parent:** `0ff481f0a6a84146fe3ac1c7fd759adb7e5b8e24`

## Purpose

Foundation 08 adds bounded retrieval to the already-accepted graph-aware CRIT path without adding a new external provider, vector model, cross-project memory, convergence detector, autonomous learning, or production scope.

This tranche implements the dependency-safe retrieval foundation:

- deterministic lexical retrieval over the current idea/project's governed application record;
- bounded depth-1 traversal of the current governed graph context;
- reproducible retrieval receipts;
- explicit retrieval provenance and safety labels;
- bounded retrieval context supplied to CRIT as data only.

Vector retrieval and embeddings require separate provider/model/data-transfer authority and are excluded from Foundation 08.

## Retrieval authority

Retrieval is candidate recall only.

A retrieval result:

- is not evidence verification;
- is not accepted graph truth;
- is not an instruction;
- cannot answer a current-project unknown by itself;
- cannot close an evidence gap;
- cannot change readiness;
- cannot approve a PRD;
- cannot create a graph mutation;
- cannot select a provider/model;
- cannot route execution;
- cannot promote or release.

CRIT may use retrieval only to focus on already-authorized material unknowns.

## Scope boundary

Retrieval scope is exactly one current `idea_id`.

The retriever may read only current durable state already authorized for that idea:

- immutable original idea title, description, and impact;
- persisted human answers and answer history;
- human-supplied evidence references;
- current evidence requirements;
- bounded Foundation 07 graph context:
  - open evidence gaps;
  - deterministic next actions;
  - graph revision and projection identity.

The retriever must reject any supplied object whose project/idea identity differs from the current idea.

Cross-project retrieval, organization-wide history, generalized memory, historical failure-pattern reuse, and cross-project learning are excluded.

## Retrieval mechanism

Foundation 08 uses:

`DETERMINISTIC_LEXICAL_V1 + GOVERNED_GRAPH_DEPTH_1`

Lexical ranking is deterministic and local. It must not use a model, remote API, embedding provider, web search, or external index.

Required bounds:

- `top_k = 6`;
- minimum lexical score > 0 for lexical-only results;
- graph traversal depth = 1;
- relationship/input set limited to the already-bounded Foundation 07 graph context;
- maximum returned result count = 6;
- maximum aggregate returned text budget = 6,000 characters;
- no full-record or full-graph dump.

Stable tie-breaking must use deterministic object identity.

## Corpus safety metadata

Every retrievable item must preserve:

- `object_id`;
- `source_type`;
- `trust_class`;
- `authority_class`;
- `data_classification`;
- `instruction_status`;
- `source_snapshot_id`;
- bounded text;
- current idea/project identity.

Foundation 08 defaults retrieved content to:

`instruction_status = DATA_ONLY`

unless an existing authoritative contract explicitly says otherwise. This tranche does not create an instruction-authority corpus.

Hostile text such as â€œignore previous instructions,â€ tool commands, policy-like wording, or model-directed content remains data and cannot alter system instructions, permissions, authority order, or graph truth.

## Retrieval query

Question selection uses a deterministic query derived from current application state, not model-generated search terms.

The query may include:

- immutable idea title and description;
- current/last answered criterion key;
- unresolved authorized candidate question keys/dimensions;
- the latest submitted human answer when present.

The exact normalized query is not required to be persisted as plaintext. Its SHA-256 digest must be in the receipt.

## Reproducible receipt

Every retrieval attempt used by CRIT must produce a receipt containing:

- schema/version;
- idea/project scope;
- mechanism identity;
- query digest;
- retrieval timestamp;
- graph revision;
- graph projection digest;
- source event hash;
- corpus snapshot digest;
- lexical index identity;
- filters;
- `top_k`;
- threshold;
- traversal depth;
- relationship/input filters;
- context/text budget;
- returned object IDs;
- deterministic ranking scores;
- result count;
- retrieval status;
- authority label `ADVISORY_RETRIEVAL_CONTEXT_ONLY`.

A compact receipt identity must be persisted on each CRIT-selected question and on the saved answer to that question.

## Availability contract

For CRIT, bounded retrieval is:

`DEGRADABLE`

Clean retrieval unavailability may degrade to the already-accepted Foundation 07 graph-aware CRIT context only when:

- no retrieval result has been consumed;
- the unavailable state is explicit;
- the current question/answer records `retrieval_status = UNAVAILABLE_DEGRADED`;
- no retrieved content is substituted from memory, web, another project, or another provider.

Unsafe retrieval state is not degradable.

The following fail closed for new question selection:

- cross-project result;
- malformed receipt;
- stale graph identity;
- stale corpus snapshot;
- result count or text budget overflow;
- unrecognized mechanism/index identity;
- missing source metadata;
- retrieval result not reproducible from current durable state.

## Provider/model boundary

Foundation 08 does not modify CRIT provider/model authority.

Hosted staging remains:

- CRIT provider: OpenAI API direct;
- CRIT model: `gpt-6-luna`;
- no fallback;
- no escalation;
- no tools;
- `store=false`.

The retriever itself has:

- no provider;
- no model;
- no secret;
- no network;
- no embedding call.

## Definition of done

Foundation 08 is PASS only if one exact application candidate proves all of the following:

1. deterministic lexical retrieval is same-idea/project scoped before ranking;
2. bounded graph traversal uses only current Foundation 07 graph context and depth 1;
3. results are capped at top 6 and aggregate text <= 6,000 characters;
4. lexical scoring and tie-breaking are deterministic;
5. every result preserves source/trust/authority/data/instruction metadata;
6. prompt-injection-like retrieved text remains `DATA_ONLY`;
7. retrieval result cannot expand the authorized CRIT question universe;
8. retrieval cannot close evidence gaps, create graph truth, approve readiness, or mutate graph state;
9. each used retrieval has a reproducible receipt with query/corpus/graph identities;
10. selected questions persist compact retrieval receipt identity;
11. saved answers preserve the retrieval receipt identity of the question answered;
12. clean retriever unavailability degrades explicitly to Foundation 07 graph-aware CRIT;
13. malformed, stale, cross-project, or over-budget retrieval fails closed;
14. reopening/restart reconstructs the same current retrieval context from durable state;
15. fresh strong/mixed/weak inputs preserve epistemic behavior;
16. targeted retrieval/CRIT tests pass;
17. full application regression passes;
18. exact-SHA application CI passes;
19. isolated Railway staging runs the exact candidate;
20. live provider/model remains `openai_api / gpt-6-luna`;
21. live retrieval receipt/currentness provenance is visible and reconciles;
22. real browser acceptance passes;
23. independent verification passes, including any required broader requalification;
24. both `main` branches and production remain untouched.

## Explicit exclusions

Foundation 08 does not authorize:

- embeddings;
- vector similarity;
- an embedding provider/model;
- pgvector, Pinecone, Weaviate, Qdrant, Elasticsearch, or another external retrieval store;
- web retrieval;
- Graphify as authority;
- cross-project retrieval;
- generalized failure-pattern learning;
- convergence/shared-root detection;
- autonomous learning;
- graph-triggered execution;
- legacy-planner removal;
- provider/model changes;
- production deployment or promotion;
- either `main` merge.

## Stop rule

Stop at the Foundation 08 acceptance boundary.

Convergence/shared-root detection remains the next roadmap capability after bounded retrieval is independently accepted. Vector retrieval remains a separately governed retrieval extension because it requires additional provider/model/data-transfer authority.

## Acceptance result

Foundation 08 is accepted on exact application candidate:

`c2b4f89d918dcf8c73bde8a490f6f42535f94038`

with Foundation 07 application parent:

`0ff481f0a6a84146fe3ac1c7fd759adb7e5b8e24`

The candidate is preserved on remote branch `candidate/foundation08-bounded-retrieval-20261004`. Qualification-app `main` remains unchanged at `32d474fdb8fe0672d826ff434b4bfc94c9537407`.

Accepted Railway staging deployment:

`c452c5ea-4850-4b36-9625-4efc0523598f`

The live deployment is SUCCESS and online with one running replica, zero crashed replicas, zero warnings, zero critical issues, and the persistent volume still present.

### Accepted retrieval mechanism

Foundation 08 accepts:

`DETERMINISTIC_LEXICAL_V1+GOVERNED_GRAPH_DEPTH_1`

with:

- same-idea/project scope before ranking;
- `top_k = 6`;
- aggregate returned text budget <= 6,000 characters;
- deterministic lexical ranking and object-ID tie-breaking;
- depth-1 use of the already-bounded Foundation 07 graph context;
- `gacm-lexical-v1` index identity;
- explicit source/trust/authority/data/instruction metadata;
- `DATA_ONLY` instruction status for retrieved content;
- reproducible receipt identity containing query, corpus, graph, index and returned-object identities.

No vector model, embedding call, external retrieval provider, retrieval secret, web retrieval, external index, or cross-project retrieval exists in this candidate.

### Verification evidence

- targeted retrieval/CRIT acceptance: **100/100 PASS**;
- full application regression: **153/153 PASS**;
- exact-SHA application CI: **PASS** on `c2b4f89...`;
- candidate audit: six expected files only, zero unexpected files, zero secret literal hits;
- live strong/mixed/weak hosted behavior: **PASS**;
- live strong case retrieval receipt returned six bounded same-project objects and was preserved exactly on the saved answer;
- mixed case remained `NEEDS_FOLLOWUP` and not ready;
- weak hostile-looking input remained `UNANSWERED` and not ready;
- prompt-injection-like content remained `DATA_ONLY`;
- clean retrieval unavailability degrades explicitly to Foundation 07 graph-aware CRIT;
- malformed, stale, cross-project and over-budget retrieval negative controls: **PASS / rejected**;
- exact process restart/reopen reconstructed the same question ID and same retrieval receipt identity from durable SQLite + graph state;
- real Microsoft Edge browser acceptance: **PASS**, showing bounded retrieval, deterministic mechanism, advisory-only authority, exact receipt digest and lexical index identity;
- local SHA == remote candidate SHA == Railway commit == served runtime SHA;
- canonical local source-tree SHA-256 == served SHA-256: `22e1f40c0a20aea8fbcd4445fb865958fd94f769dfc18beff5b545dc9fa3c6a3`;
- live CRIT provider/model remained `openai_api / gpt-6-luna`;
- production mutation: **NONE**.

### Independent verification

GACM verifier `gacm-independent-verifier-v1` issued authoritative **PASS**:

`verify-d52d595d6693ec66b7f101d1`

The exact delta is correctly classified `MODEL_BEARING` because the CRIT selection prompt changed. Broader requalification was required and completed with the 153/153 full regression, 100/100 targeted retrieval/CRIT suite, live strong/mixed/weak OpenAI `gpt-6-luna` behavior, retrieval safety negative controls, process restart/reopen proof, exact currentness proof, and real Edge acceptance.

### Acceptance decision

All 24 Foundation 08 definition-of-done items are satisfied.

Foundation 08 therefore closes **PASS** at the accepted staging-candidate boundary.

Convergence/shared-root detection is the next roadmap capability. It is not opened by this acceptance. Vector/embedding retrieval also remains a separate governed extension requiring explicit provider/model/data-transfer authority.
