# GACM Graph Application Runtime Integration v1

**Status:** ACCEPTED — FOUNDATION 05 TRANCHE BOUNDARY
**Authorized:** 2026-10-03
**Accepted:** 2026-10-03

## Purpose

Bind the accepted durable governed graph engine to the actual GACM qualification application without allowing the application, browser, SQLite record, semantic reviewer, or graph projection to create new governance authority.

## Governing engine authority

Repository:

`chriskulbaba2025/gacm-trial`

Foundation 04 engine SHA:

`4ecc2ead93f185bb563b99ca87580c0d90a69e27`

Branch:

`governance/gacm-graph-foundation-04-persistence-20261003`

## Application authority

Repository:

`chriskulbaba2025/gacm-qualification-sandbox`

Starting Phase 16 candidate:

`132cff6d3280e3fe8f86b23a0113cab986df03e3`

Accepted Foundation 05 application candidate:

`19028a49b89a00be718ee017149a7615e966e4fd`

Branch:

`candidate/foundation05-durable-graph-runtime-20261003`

Application exact-SHA CI:

- workflow: `Qualification App Regression`
- run: `37160293393`
- conclusion: PASS
- head SHA: `19028a49b89a00be718ee017149a7615e966e4fd`

## Engine vendoring boundary

The application remains standalone and has no Python dependency manager or pre-existing governed package-distribution path.

Foundation 05 therefore vendors the exact Foundation 04 `src/gacm` tree into:

`vendor/gacm_engine/src/gacm`

The vendor manifest binds:

- source repository;
- source branch;
- exact GACM SHA;
- vendored scope;
- exact file set;
- canonical Git-text SHA-256 and byte identity for every source file.

Canonical manifest identity:

`26b1378022b1558651aec0f9e1595f318d35b965b178e1bba6b87af9ab22b778`

Runtime validation occurs at process import and again on every graph synchronization.

Line ending differences between Windows CRLF and Linux LF are normalized to canonical Git text before identity comparison. This prevents checkout platform from becoming an authority difference.

A vendor file, manifest, repository, branch, SHA, scope, file-set, or content mismatch fails the graph runtime closed.

## Application / graph authority separation

SQLite remains the durable application implementation record.

The graph is a separately durable governed control projection.

The graph may read validated application state but may not rewrite the SQLite idea record.

A graph failure cannot roll back or corrupt an already committed SQLite application record.

Graph-dependent reads retry projection and fail closed when the projection cannot be validated.

## Projection model

One graph file exists per idea.

Foundation 05 projects:

- immutable original idea identity as a `UserNeed` in `USER_STATED`;
- deterministic open evidence requirements as `EvidenceGap` nodes in `UNKNOWN`;
- application PRD approval state as an observed `HumanApproval`;
- one qualification `Tranche`;
- deterministic `BLOCKED_BY` relationships;
- one projection marker binding the exact source event/artifact state.

Raw idea title and description are not duplicated into the graph file. The original application SHA-256 is retained as provenance.

Unverified references do not close evidence gaps.

User answers do not automatically become `EVIDENCED` or `ACCEPTED`.

Fast Filter, CRIT semantic review, and model output do not become graph authority.

PRD approval projection does not create release authority.

Obsolete evidence-gap generations are superseded when a new analysis generation replaces them.

A graph file containing another idea's project scope fails closed.

## HTTP boundary

The application exposes:

`GET /api/ideas/{idea_id}/graph`

The response is bounded to:

- graph runtime schema/status;
- idea ID;
- exact GACM engine SHA;
- canonical engine manifest identity;
- application runtime Git/source-tree identity;
- graph revision;
- projection digest;
- source event hash;
- node/edge counts;
- deterministic GraphScheduler next actions.

No credential or local filesystem path is exposed.

## Browser boundary

The real idea page shows:

- governed graph revision;
- number of eligible next actions;
- HOLD when graph projection is unavailable;
- bounded graph details in the technical audit trail.

The UI explicitly says graph actions are deterministic eligibility signals, not autonomous human, verification, model, provider, or release decisions.

## Acceptance evidence

Application targeted graph/browser/CLI portability tests:

25/25 PASS.

Complete application regression:

125/125 PASS.

Exact-SHA GitHub application CI:

PASS at `19028a49b89a00be718ee017149a7615e966e4fd`.

Real local HTTP/browser acceptance used the actual application server and headless Microsoft Edge.

Fresh accepted-browser idea:

- graph status PASS;
- initial graph revision 2;
- browser-rendered graph revision 3 after the governed interview initialization event;
- six `CLOSE_EVIDENCE_GAP` actions;
- one `HUMAN_APPROVAL` action;
- exact engine SHA visible;
- no browser request failure;
- screenshot produced.

The graph file did not contain the unique raw title or description used by the browser smoke.

The application server was then terminated and restarted against the same SQLite database and graph directory.

After restart:

- application idea reloaded;
- graph status PASS;
- graph revision remained 3;
- exact application SHA remained `19028a49b89a00be718ee017149a7615e966e4fd`;
- the same six evidence-gap and one human-approval actions remained.

## Portability failure and repair

The first remote application CI run at app SHA `8503dd2a50ce386fb8a5ec9eeefa513306576ba4` failed.

The failure exposed:

1. vendor manifest/source identity had been derived from Windows checkout bytes and therefore differed after Git LF normalization on Linux;
2. two existing Codex CLI tests relied on the local Windows CLI being discoverable even though subprocess execution itself was mocked.

Foundation 05 made one bounded portability repair:

- vendor authority now uses canonical Git-text identity independent of CRLF/LF checkout representation;
- an explicit CRLF/LF equivalence regression was added;
- the existing CLI tests now mock CLI discovery as well as execution.

No semantic reviewer runtime behavior was changed.

The repaired exact candidate `19028a49...` passed local regression and exact-SHA Linux CI.

## Explicit exclusions

Foundation 05 does not implement or authorize:

- graph-driven CRIT question selection;
- browser-triggered PilotHarness execution;
- graph-triggered model execution;
- retrieval;
- graph convergence/shared-root detection;
- cross-project learning;
- legacy planner removal;
- application `main` merge;
- GACM `main` merge;
- production deployment;
- production promotion.

## Hosted staging boundary

At Foundation 05 start, the qualification application repository contained no hosted deployment configuration and no durable authority selecting a hosting provider/account/environment.

Foundation 05 therefore did not infer a provider from ambient tools, available accounts, convenience, or price.

The actual application/runtime/browser path is proven locally.

A hosted staging environment now requires a separate governed deployment tranche that first establishes:

- authoritative hosting provider;
- account/project/environment identity;
- credential provenance;
- staging URL/currentness identity;
- deployment/release contract;
- real hosted browser acceptance.

Hosted staging must remain separate from production promotion.
