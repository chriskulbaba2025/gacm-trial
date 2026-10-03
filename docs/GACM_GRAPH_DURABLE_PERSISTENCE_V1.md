# GACM Durable Governed Graph Persistence v1

**Status:** IMPLEMENTATION CANDIDATE
**Authorized:** 2026-10-03
**Starting authority:** `25d67953c465abe91b2ad0f5e9378e24e78dcb45`

## Purpose

Persist the governed GACM graph across process restart without creating a second authority path.

The durable store must preserve the exact graph state needed by `GraphScheduler` while keeping normal graph mutation invariants authoritative.

## Core invariant

Durable storage is not graph truth by itself.

A persisted graph becomes usable only after:

`READ BYTES → VERIFY FORMAT/DIGEST → REPLAY GOVERNED MUTATIONS → REBUILD RECEIPTS/IDEMPOTENCY → CROSS-CHECK PROJECTION → RETURN GRAPH`

Not:

`READ JSON → TRUST CURRENT NODES/EDGES`

## Runtime boundary

The implementation lives in:

`src/gacm/graph/persistence.py`

Public adapter:

`JsonGovernedGraphStore`

The in-memory `GovernedGraph` remains the invariant and mutation authority.

## Persisted record

The durable record contains:

- format identity;
- schema version;
- full unfiltered graph snapshot;
- exact graph revision;
- current nodes;
- current edges;
- complete mutation history;
- mutation receipts;
- deterministic payload digest.

Project-filtered snapshots are not valid durable graph stores.

## Reconstruction

`load()` creates a new `GovernedGraph` and replays every persisted `GraphMutation` through normal `GovernedGraph.apply()`.

Load fails closed if:

- JSON is unreadable or malformed;
- format or schema is unsupported;
- required keys differ;
- persisted field types are invalid;
- payload digest differs;
- mutation and receipt counts differ;
- mutation expected revisions are not contiguous;
- any mutation fails normal graph invariants;
- replayed revision differs from the persisted revision;
- replayed receipts differ from persisted receipts;
- replayed nodes/edges/history differ from the persisted projection.

Private in-memory state is never injected directly during reconstruction.

## Idempotency and replay

Reconstruction rebuilds the normal `GovernedGraph` idempotency map by replay.

After restart:

- replaying an identical mutation remains idempotent;
- reusing an idempotency key with different content remains rejected;
- the next valid mutation must continue from the reconstructed revision.

## Durable mutation boundary

`JsonGovernedGraphStore.apply(mutation)`:

1. acquires the exclusive durable writer lock;
2. loads and replay-validates the current graph, or starts a new graph if none exists;
3. applies the mutation through normal graph invariants;
4. replay-validates the resulting candidate;
5. atomically persists the resulting durable graph;
6. returns both mutation and persistence receipts.

This is the preferred mutation path when durability is required.

## Currentness / stale-writer control

Direct `save()` requires `expected_stored_revision`.

Rules:

- first save requires no existing durable graph and `expected_stored_revision = None`;
- updates require the exact current stored revision;
- a missing durable graph when a revision is expected fails;
- an older candidate fails;
- divergent mutation history fails;
- same-revision different content fails.

The candidate history and receipts must extend the already durable history.

## Concurrent writers

The store uses a cross-platform non-blocking OS file lock around the full read/check/write boundary.

Only one process may own the durable writer boundary at a time.

A competing writer fails closed with `GraphPersistenceLocked`.

The OS releases the advisory lock when the owning process exits; the lock marker file itself is not authority.

## Atomic write

Writes use:

1. a same-directory temporary file;
2. file flush + `fsync`;
3. atomic `os.replace`;
4. best-effort parent-directory `fsync`.

Readers therefore see either the prior complete record or the new complete record, not a partially written JSON document.

## Candidate validation before write

The store replay-validates the candidate snapshot before first persistence or replacement.

A corrupted or privately manipulated in-memory `GovernedGraph` cannot be made durable merely by calling `save()`.

## Integrity is not new authority

The payload digest detects byte/content inconsistency. It is not a human, release, provider, verification, or cryptographic signing authority.

Persistence does not upgrade epistemic state and does not create:

- `EVIDENCED`;
- `ACCEPTED`;
- verification PASS;
- release authority;
- provider authority;
- model authority;
- human approval.

Those remain governed by their existing GACM boundaries.

## Scheduler continuity

After successful reconstruction, `GraphScheduler` consumes the reconstructed graph normally.

Acceptance requires equivalent scheduler action identities before and after restart for the same durable graph revision.

Foundation 03B planning currentness checks continue to use the reconstructed graph revision.

## Proven restart behavior

Acceptance includes a real fresh Python process that:

- opens the durable graph record;
- reconstructs it through mutation replay;
- confirms the exact revision and snapshot digest;
- derives the same GraphScheduler action set.

## Explicit exclusions

Foundation 04 does not implement:

- PostgreSQL, pgvector or Neo4j;
- lexical/vector retrieval;
- graph-aware CRIT;
- convergence/shared-root detection;
- cross-project learning;
- automatic legacy-planner removal;
- application deployment;
- production graph migration;
- merge to `main`.

## Next boundary

After Foundation 04 is independently accepted, application/runtime wiring of this durable graph into the actual GACM app and staging/browser path must be a separate governed tranche.

That tranche must not silently combine runtime wiring with retrieval, graph-aware CRIT, convergence, legacy-planner removal, broad V2 migration, or production promotion.
