# GACM Graph Foundation 07 — Graph-Aware CRIT v1

**Status:** PASS — ACCEPTED STAGING CANDIDATE / STOP AT FOUNDATION 07 BOUNDARY
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

## Acceptance result

Foundation 07 is accepted on exact application candidate:

`0ff481f0a6a84146fe3ac1c7fd759adb7e5b8e24`

Application parent remains promoted MVP `main` SHA:

`32d474fdb8fe0672d826ff434b4bfc94c9537407`

The candidate is preserved on remote branch `candidate/foundation07-graph-aware-crit-20261003`. Qualification-app `main` remains unchanged at the MVP authority SHA; Foundation 07 is an accepted isolated staging candidate, not a new application promotion.

Accepted Railway staging deployment:

`65dbc434-cdcb-461d-8805-80612bce29d4`

Provider/model remained unchanged: OpenAI API direct / `gpt-6-luna`. No credential, domain, volume, resource-limit, start-command, production, retrieval, convergence, or execution-authority change occurred.

### Verification evidence

- targeted graph/CRIT acceptance: **90/90 PASS**;
- explicit Foundation 07 graph-aware tests including fresh strong/mixed/weak path: **8/8 PASS**;
- full application regression: **144/144 PASS**;
- exact-SHA application CI: **PASS** on `0ff481f0...`;
- Railway deployment: **SUCCESS**, online, 1/1 running, zero crashes, zero warnings/criticals, persistent volume present;
- local SHA == remote candidate SHA == Railway commit == served runtime SHA;
- local canonical source-tree SHA-256 == served SHA-256: `9fb5d0f5afa27aca65e7068bc9da41b092a5c64a350597526511a433f95838f8`;
- hosted graph status: **PASS**;
- hosted CRIT graph context: **AVAILABLE**;
- hosted question status: **READY**;
- live reviewer provider/model: `openai_api / gpt-6-luna`, tools false, store false;
- real Microsoft Edge acceptance: **PASS** with CRIT graph context, advisory authority, graph revision and exact projection digest visible; no request-failure or `REVIEW_UNAVAILABLE` text;
- production mutation: **NONE**.

### Live graph-aware evidence

Fresh hosted strong, mixed, and weak ideas all traversed the graph-aware CRIT path.

The strong case selected `evidence_plan` rather than mechanically starting at `first_user`, demonstrating that CRIT can reprioritize within the existing authorized candidate universe. Its selected question persisted graph revision 3, exact projection digest, source event hash, and engine authority SHA; the same identity was preserved on the saved answer. The real semantic reviewer returned `NEEDS_FOLLOWUP`; that result is preserved rather than forced to a desired classification.

The mixed case remained `NEEDS_FOLLOWUP` and not ready. The weak case preserved `UNANSWERED`, “I don't know yet.”, and not-ready state. All reopened with graph context AVAILABLE.

### Independent verification and broader requalification

GACM verifier `gacm-independent-verifier-v1` issued authoritative **PASS**:

`verify-d7575320fe6573daa44cbe7f`

The exact delta was correctly classified `MODEL_BEARING` because `crit_review.py` changed. Broader requalification was therefore required. It was completed using the full 144/144 regression, 8/8 fresh graph-aware generalization, live OpenAI `gpt-6-luna` graph-context provenance, release-currentness identity proof, and real Edge acceptance. No model or provider identity changed.

### Acceptance decision

All 18 Foundation 07 definition-of-done items are satisfied. Foundation 07 therefore closes **PASS** at the accepted staging-candidate boundary.

Bounded retrieval remains the next roadmap item, but it is not part of Foundation 07 and is not implicitly started by this acceptance.
