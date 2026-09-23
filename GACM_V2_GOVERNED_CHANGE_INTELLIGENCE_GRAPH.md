# GACM Version 2 — Governed Change Intelligence Graph

Status: Future-state architecture authority / roadmap detail
Repository: chriskulbaba2025/gacm-trial
Purpose: Define the governed reasoning-graph architecture for GACM Version 2 without changing the current accepted runtime baseline.

## 1. Architectural objective

Version 2 should add a governed reasoning graph between CRIT/GACM reasoning and worker execution.

Target lifecycle:

    Idea/change
    → CRIT
    → hybrid retrieval
    → governed reasoning graph
    → question/decision
    → PRD
    → tranche planner
    → worker execution
    → evidence/test results
    → graph update
    → next reasoning cycle
    → release
    → SETTLE
    → reusable learning

The graph does not replace durable authority, operational state, source discovery, artifacts, release identity, or independent verification.

Authority separation:

    GitHub / approved durable authority
        source, governance, release, and approved artifact authority

    Operational relational store
        current workflow and application state within its governed authority scope

    Governed reasoning graph
        relationships, reasoning memory, accepted derived knowledge, and evidence links

    Artifact store
        proofs, files, logs, reports, builds, screenshots, and large outputs

    Graphify
        discovery of source/code relationships only

    Vector + lexical retrieval
        candidate recall only

    CRIT / GACM
        reasoning and governance

    Worker
        bounded execution

The graph is a governed projection. A graph assertion never outranks its authoritative source.

Graphify remains discovery-only. It must not become the GACM reasoning graph or authority layer.

## 2. Durable reasoning object model

The graph should contain durable reasoning objects that can materially improve later questioning, planning, repair, verification, or release decisions.

Initial node classes:

    Requirement
    BusinessGoal
    UserNeed
    Assumption
    Unknown
    Evidence
    EvidenceGap
    Decision
    Constraint
    Risk
    Dependency
    Defect
    RootCause
    FailurePattern
    Change
    Test
    Gate
    Artifact
    System
    Component
    Contract
    StateTransition
    Tranche
    HumanApproval
    ReleaseIdentity

Initial relationship classes may include:

    Requirement DEPENDS_ON Requirement
    Requirement AFFECTS Component
    Requirement VERIFIED_BY Test

    Evidence SUPPORTS Decision
    Evidence CONTRADICTS Assumption
    Evidence OBSERVED_IN Artifact

    Defect OBSERVED_IN Component
    Defect POSSIBLY_CAUSED_BY RootCause
    Defect MAY_SHARE_CAUSE_WITH Defect

    RootCause AFFECTS Contract
    RootCause EXPLAINS Defect

    Change ADDRESSES Defect
    Change AFFECTS Component
    Change REQUIRES Test

    Test VERIFIES Requirement
    Test DETECTED Defect

    Gate BLOCKED_BY EvidenceGap
    Gate REQUIRES HumanApproval
    Gate VERIFIED_BY Evidence

    FailurePattern EXEMPLIFIED_BY Defect
    RootCause MATCHES FailurePattern

    Decision SUPERSEDES Decision
    Decision BASED_ON Evidence

    Tranche IMPLEMENTS Requirement
    Tranche DEPENDS_ON Tranche

    ReleaseIdentity SERVES EntryPoint
    ReleaseIdentity USES RuntimeConfiguration

The graph vocabulary is versioned governance data. Workers may propose new graph objects or relationships but may not silently invent new authoritative relationship types.

## 3. Epistemic state applies to nodes and edges

Every graph node and every graph edge must have an epistemic state.

Minimum states:

    USER_STATED
    OBSERVED
    EVIDENCED
    INFERRED
    HYPOTHESIS
    CONFLICTED
    ACCEPTED
    SUPERSEDED
    UNKNOWN

Every graph object must also carry, where applicable:

    object_id
    project_id
    organization_id
    run_id
    object_type
    source
    provenance
    authority_ref
    authority_digest
    source_snapshot_id
    status
    epistemic_state
    confidence
    created_at
    valid_from
    valid_to
    superseded_by
    schema_version
    producer_role
    verification_state

Confidence is not authority. A high-confidence inference remains an inference until the applicable evidence/governance rule promotes it.

ACCEPTED means accepted for a defined scope and version. It does not mean permanently true.

## 4. Blind spot correction — causal claims need a higher proof standard

Similarity, co-occurrence, shared components, shared contracts, vector matches, and repeated historical patterns may produce:

    POSSIBLE_SHARED_ROOT_CAUSE

or a POSSIBLY_CAUSED_BY relationship.

They may not automatically produce authoritative CAUSED_BY, ROOT_CAUSE, or equivalent causal truth.

An authoritative root-cause relationship requires:

- explicit supporting evidence;
- provenance;
- an owning contract or mechanism;
- a falsifiable explanation where practical;
- verification appropriate to blast radius;
- independent verification when the causal claim is used to close a governed repair.

This prevents the reasoning graph from turning correlation into product truth.

## 5. Blind spot correction — provenance, time, currentness, and invalidation

Every graph object must resolve to the source snapshot from which it was derived.

When a governing source changes, GACM must determine whether affected graph objects remain current.

Stale graph context must not silently govern a new run.

At minimum, graph currentness should consider:

- authoritative source SHA or content digest;
- governing PRD or contract revision;
- release identity;
- schema revision;
- operational context revision;
- environment;
- project/tenant identity;
- evidence artifact digest;
- relevant model/provider identity when the object depends on model-produced interpretation.

The graph must integrate with GACM-RELEASE-CURRENTNESS-AND-IDENTITY-GATE.

A release or source identity change can invalidate graph assertions that depended on the prior identity.

Invalidation preserves history. It must not delete the old reasoning record.

## 6. Transactional graph mutation contract

Do not write model thoughts directly into durable graph authority.

Graph updates follow:

    1. retrieve bounded current context
    2. reason
    3. emit proposed graph mutations
    4. validate schema, provenance, permissions, scope, and invariants
    5. require human / governance / independent-verifier acceptance where applicable
    6. atomically commit accepted mutations
    7. execute governed work
    8. collect evidence
    9. independently verify
    10. append verified outcomes and supersession/invalidation events

Each mutation requires:

- immutable mutation ID;
- actor/producer role;
- prior graph revision;
- proposed changes;
- evidence references;
- authority references;
- project/tenant scope;
- idempotency key;
- timestamp;
- validation result;
- acceptance result;
- resulting graph revision.

Mutation history is append-only.

The graph runtime must reject stale-write conflicts, replayed mutations, unauthorized writers, and cross-project writes.

## 7. Blind spot correction — graph consistency and concurrency

The graph layer must enforce structural invariants rather than relying only on LLM behavior.

Controls should include:

- optimistic locking or equivalent revision checks;
- idempotent mutation application;
- replay protection;
- edge endpoint existence;
- project/tenant scope compatibility;
- legal epistemic-state transitions;
- legal supersession relationships;
- cycle detection where cycles are prohibited by relationship contract;
- bounded cardinality where relationship explosion would make reasoning unreliable;
- schema migration and backward-compatibility rules;
- durable audit history.

A valid graph snapshot alone does not prove a valid mutation history.

## 8. CRIT graph-aware questioning

CRIT should query the graph before asking a material question.

Target loop:

    current decision
    → retrieve relevant governed context
    → identify material uncertainty/gap
    → ask highest-value question
    → update governed state
    → repeat

Question selection should consider:

- unresolved requirements;
- contradictory evidence;
- missing evidence;
- affected components/contracts;
- prior decisions;
- known dependencies;
- related historical failure patterns;
- open risks;
- state transitions;
- release/currentness constraints.

Historical context may improve question quality but may not answer the current project's question automatically.

CRIT should not ask for information the current authoritative graph already proves.

CRIT must still ask when historical similarity exists but current-project evidence is missing.

## 9. Hybrid retrieval contract

Version 2 should use:

    vector retrieval + lexical lookup + bounded graph traversal

Each mechanism has a different role:

- lexical lookup finds exact identifiers, contracts, terms, IDs, and known failure-pattern names;
- vector retrieval finds semantically similar candidate material;
- graph traversal follows already-governed relationships.

Vector similarity never creates graph truth.

Hybrid retrieval must produce a reproducible receipt containing, where applicable:

    project/tenant scope
    query or query digest
    retrieval timestamp
    graph revision
    source/corpus snapshot
    embedding model/provider/version
    lexical index identity
    filters
    top-k / thresholds
    returned object IDs
    ranking scores
    traversal depth
    relationship filters
    token/context budget

Retrieval must be bounded. Returning all related history is a defect, not better context.

A retrieval result is context for reasoning, not authority.

## 10. Blind spot correction — retrieval safety and prompt injection

Evidence, documents, logs, issue text, web content, user input, and historical artifacts may contain hostile or irrelevant instructions.

Retrieved content must be treated as data unless its source is explicitly an instruction authority.

The graph/retrieval layer must preserve:

- source type;
- trust class;
- authority class;
- data classification;
- instruction/non-instruction status.

Retrieved text may not rewrite GACM governance, change tool permissions, change authority order, or self-promote to accepted graph truth.

## 11. Convergence and shared-root detector

Version 2 should include a convergence detector.

When multiple defects, risks, or requirements share one or more of:

- component;
- governing contract;
- dependency;
- evidence lineage;
- workflow/journey boundary;
- state transition;
- API;
- schema;
- identity boundary;
- persistence boundary;
- release identity;
- failure pattern;

GACM may flag:

    POSSIBLE_SHARED_ROOT_CAUSE

That flag requires diagnosis at the shared owning boundary before independent symptom repairs are accepted.

The detector must record why convergence was flagged.

It must not claim a shared root cause solely from graph proximity or vector similarity.

This capability directly strengthens GACM-GENERALIZATION-AND-WHOLE-SYSTEM-GATE and its protection against SEQUENTIAL_BLOCKER_TUNNELING.

## 12. Historical failure-pattern learning

Reusable failure patterns become first-class governed graph objects.

A failure pattern should contain:

- stable pattern identity;
- scope;
- signals;
- anti-signals;
- known mechanisms;
- prior independently verified occurrences;
- prevention guidance;
- tests that detect it;
- known false positives;
- provenance;
- currentness;
- generalization status.

Generalization status should be explicit:

    PROJECT_LOCAL
    CANDIDATE_GENERALIZED
    GENERALIZED
    SUPERSEDED

A project-local failure may not silently become universal learning.

Promotion to generalized reusable knowledge requires independent evidence that the pattern applies beyond the originating fixture/project and a governance approval appropriate to its impact.

Cross-project learning shares the generalized pattern, not confidential project evidence.

## 13. Blind spot correction — tenant, privacy, and authorization boundaries

Graph traversal and retrieval must preserve the same organization/project/user boundaries as the governed product.

Required controls include:

- tenant/project filters applied before retrieval, not after;
- row/object-level authorization where required;
- no cross-project evidence leakage;
- no embedding or external-model transfer of restricted evidence unless permitted by data policy;
- data-retention and deletion rules;
- redaction/de-identification before approved cross-project learning;
- auditable human approval where a reusable pattern contains sensitive operational knowledge.

A correct answer obtained through unauthorized graph traversal is still a governance failure.

## 14. Blind spot correction — rollback and reconstruction

Graph state must participate in rollback and reconstruction.

A governed rollback must record:

- source/runtime rollback target;
- graph revision before rollback;
- graph revision after rollback/reconciliation;
- objects invalidated by rollback;
- objects retained as historical evidence;
- release-currentness impact;
- reconstruction proof.

Rollback must not erase the knowledge that a failed candidate existed.

A new process/chat must be able to reconstruct the same authoritative current context from durable state without relying on conversation memory.

## 15. Blind spot correction — graph availability and degraded behavior

The graph is valuable but must not become an unbounded single point of failure.

Each GACM capability must declare whether graph availability is:

    REQUIRED
    DEGRADABLE
    OPTIONAL

If the graph is unavailable:

- authority must not be guessed from memory;
- graph-dependent gates fail closed;
- optional historical-learning features may degrade safely;
- execution may continue only when the frozen work-unit contract permits operation without graph-derived context;
- the degraded state must be explicit in evidence.

No silent fallback from governed graph evidence to model memory is permitted.

## 16. Release identity observability for graph-backed reasoning

Where graph context contributes materially to acceptance or release, the release proof should identify:

- graph schema version;
- graph revision;
- current authoritative source identities;
- retrieval/index versions;
- relevant generalized-pattern version;
- release SHA/environment/build identity.

This makes it possible to answer both:

"Which exact release is this browser running?"

and:

"Which exact governed reasoning state contributed to this release decision?"

without inference.

## 17. Storage architecture

Initial implementation preference:

PostgreSQL + pgvector, with relational operational tables kept separate from graph/reasoning tables.

Suggested reasoning tables:

    gacm_graph_nodes
    gacm_graph_edges
    gacm_graph_evidence
    gacm_graph_embeddings
    gacm_graph_mutations
    gacm_graph_revisions
    gacm_retrieval_receipts

The storage contract is more important than the vendor.

A later move to a dedicated graph database must not change authority, provenance, isolation, mutation, or epistemic rules.

The graph must never become the sole storage system.

## 18. Independent verification of graph assertions

The execution worker may propose graph mutations but may not authoritatively verify its own high-impact graph assertions.

Independent verification must be able to challenge:

- provenance;
- authority resolution;
- epistemic state;
- causal claims;
- currentness;
- project/tenant isolation;
- supersession;
- failure-pattern generalization;
- retrieval scope;
- convergence claims;
- graph-derived repair scope.

A graph assertion used to satisfy a release or repair gate must be independently verifiable from durable evidence.

## 19. Adversarial acceptance requirements

The governed change-intelligence graph is not complete until adversarial tests prove at minimum:

- hypotheses cannot silently become accepted facts;
- inferred edges cannot silently become evidenced edges;
- vector similarity cannot create relationships;
- correlation cannot silently become root cause;
- historical project evidence cannot become current-project evidence;
- project A cannot retrieve project B's restricted evidence;
- fixture-specific knowledge cannot become generalized learning without the required gate;
- superseded decisions remain historically visible but stop governing current execution;
- source changes invalidate stale dependent graph assertions;
- graph rollback preserves historical evidence while restoring current authority;
- concurrent writers cannot silently overwrite one another;
- replayed mutations do not duplicate state;
- malformed or unauthorized mutations fail closed;
- Graphify discovery cannot become authority;
- retrieval cannot overwhelm CRIT with unbounded irrelevant context;
- prompt-injected source evidence cannot change governance;
- embedding/model changes do not silently change accepted authority;
- graph state survives restart/chat loss;
- durable reconstruction reproduces the same current authoritative context;
- convergence detection finds planted shared-boundary failures without claiming unsupported causality;
- worker agents cannot modify graph governance rules;
- independent verification can reject executor-authored graph claims;
- release-currentness evidence identifies the graph revision that supported the accepted release.

## 20. What the graph must not contain by default

Do not build a graph of:

- every source-code symbol;
- every worker/Codex message;
- private chain-of-thought;
- every test log line;
- every file;
- every transient hypothesis;
- every model response;
- every runtime event.

Graphify/source tooling handles source topology.

Artifact storage handles logs and large evidence.

Run state handles execution state.

The governed reasoning graph stores durable reasoning objects and relationships that materially affect later decisions.

## 21. Version 2 implementation order

Recommended order:

1. Governed reasoning graph schema and authority boundary.
2. Graph mutation/provenance/currentness contract.
3. Tenant/security and transactional mutation enforcement.
4. Graph revision, reconstruction, rollback, and invalidation.
5. CRIT graph-aware questioning.
6. Lexical retrieval.
7. Vector retrieval with reproducible retrieval receipts.
8. Bounded graph traversal.
9. Convergence/shared-root detection.
10. Historical failure-pattern retrieval.
11. PRD/tranche generation from graph.
12. Graph-aware repair planning.
13. Independent verification of graph assertions.
14. Cross-project generalized learning gate.
15. Release-currentness integration and graph observability.
16. Only then consider Laya or other low-cost routing/classification assistance.

Do not introduce Laya or an equivalent classifier as an authority layer.

## 22. Version 2 graph acceptance definition

The graph upgrade is complete only when it demonstrates that governed graph context improves decision/question quality or defect prevention while preserving authority, provenance, isolation, reconstructability, release identity, and human judgment.

A graph that adds context but makes authority harder to prove is a regression.

A graph that finds more historical material but increases irrelevant context enough to degrade CRIT is a regression.

A graph that improves one known fixture without generalized evidence fails GACM-GENERALIZATION-AND-WHOLE-SYSTEM-GATE.

## 23. Authorization status

This document is Version 2 architecture authority and roadmap intent only.

It does not authorize implementation, production mutation, paid provider calls, new infrastructure, embedding-provider data transfer, or migration of current GACM state.

Implementation requires a separately approved governed PRD/tranche beginning from the latest authoritative GACM release and must satisfy all current mandatory gates, including generalization/whole-system and release-currentness/identity controls.
