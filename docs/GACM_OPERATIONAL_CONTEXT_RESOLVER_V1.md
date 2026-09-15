# GACM Pilot v1 — Authoritative Operational Context Resolver

**Phase:** 5 — Authoritative Operational Context Resolver
**Module:** `src/gacm/context/`
**Core invariant:** Known authoritative operational data is resolved before model execution. The model cannot substitute, infer, or request a known value again.

## Purpose and authority rules

The resolver turns a requested operation plus a set of candidate facts into one immutable, provenance-bearing operational-context snapshot or a fail-closed `BLOCKED`/`AMBIGUOUS` result.

The authority chain is:

```text
Graphify discovers candidate
        ↓
Phase 3 GitHub resolver proves repository/ref/HEAD/files
        ↓
Phase 4 handoff proves candidate source in exact Git HEAD
        ↓
Phase 5 resolves exactly one value per required field
        ↓
later execution receives immutable verified snapshot
```

GitHub-backed durable state is the authority. Graphify, model output, chat memory, filesystem guesses, and prior conversational values are not authority. The resolver requires `ResolutionResult.status == VERIFIED` from the Phase 3 resolver and `SourceProvenance.source_kind == GITHUB` with `github_proof == true` for every material candidate.

## Required identity classes

`OperationRequirements` supports these fields:

- `project`
- `client`
- `repository`
- `branch`
- `environment`
- `cloud_account` (normally `{provider, account_id}`)
- `tenant`
- `region`
- `deployment_target`
- `service`
- `database`
- `credential_reference`
- `domain`
- `external_integration_identity`

The caller explicitly declares which fields the operation requires and may declare expected project, repository, and environment identities. Required fields are unique and must be resolved exactly once.

## Provenance requirements

Each `ContextCandidate` contains one field, one value, and `SourceProvenance` with:

- source kind;
- source path;
- source blob SHA;
- source Git HEAD SHA;
- repository identity;
- project identity;
- environment where relevant;
- optional discovery query;
- explicit `github_proof` marker.

The resolver verifies that the candidate source is a safe relative path, exists in the exact verified Git HEAD, and has the claimed blob SHA. It also verifies that source repository/project/environment provenance matches the operation and the Git authority result. Every field in a verified snapshot has one corresponding source record.

## Status model

| Status | Meaning | Execution allowed? |
|---|---|---|
| `VERIFIED` | Exactly one GitHub-backed value exists for each required field and all identity/source checks pass. | Only a later governed execution layer may decide, using this immutable snapshot. |
| `BLOCKED` | Required authority is missing, unverified, placeholder-bearing, stale, contaminated, or otherwise invalid. | No. |
| `AMBIGUOUS` | More than one valid authoritative candidate remains for a required field. | No. |

The resolver never asks the model to select between candidates. It never returns a fallback value. A non-`VERIFIED` result cannot be overridden by an executor or model.

## Missing, ambiguous, and placeholder data

Missing required fields produce `BLOCKED`. Multiple candidates for one required field produce `AMBIGUOUS`. A Graphify candidate without GitHub proof, a chat-memory-only value, or a candidate from another project/repository/environment produces `BLOCKED`.

Known placeholders and examples such as `<ACCOUNT_ID>`, `YOUR_ACCOUNT`, `YOUR_REGION`, `YOUR_REPO`, `replace_this`, `insert_your`, `example-*`, and `default-*` are rejected recursively, including inside structured cloud-account values. The resolver does not request the value again and does not guess it.

## Cross-project contamination prevention

Before accepting any value, the resolver checks:

1. GitHub authority is verified for the governed repository and HEAD.
2. Candidate source Git HEAD equals that verified HEAD.
3. Candidate source repository equals the verified repository identity and any expected repository.
4. Candidate source project equals the expected project, and a project value equals its source project provenance.
5. Candidate source environment equals the expected environment, and an environment value equals its source environment provenance.
6. Repository and project values cannot be substituted independently of their source provenance.

A candidate from another project or repository is rejected even if its field value looks plausible. The resolver has no “closest project” or “same-name” fallback.

## Immutability and authority changes

`ContextSnapshot` is a frozen dataclass with recursively frozen values and sources. A work unit can retain the snapshot’s `context_id`, `context_revision`, authority HEAD, and source blob SHAs. Attempting to mutate nested values fails.

`assert_unchanged()` compares the bound authority HEAD and source blob SHAs. If a source changes, the current unit does not silently inherit the new value; the caller must create a new verified snapshot or invalidate/requalify the unit according to later orchestration policy.

The snapshot is immutable evidence of what was resolved, not a live pointer to mutable configuration.

## Graphify and GitHub roles

Graphify may locate a likely source and relationship, but it cannot establish authority. Phase 4’s handoff or equivalent proof must confirm the source exists in the exact verified Git HEAD. The resolver consumes only that GitHub-backed proof.

The resolver does not install or execute Graphify, and it does not implement the Phase 4 discovery adapter. It also does not make semantic claims about the source content beyond path/blob identity.

## Handoff to model execution

The resolver’s `VERIFIED` snapshot is the only permitted identity input for a later execution adapter. A later execution layer must:

- bind the snapshot to the work-unit identity;
- pass canonical values/references rather than asking the model to choose them;
- prevent model/tool requests from replacing those values;
- stop if the snapshot is absent, stale, or invalidated;
- record the snapshot ID and revision in durable run state.

This phase does not implement model routing or execution permissions.

## Phase 2 run-state integration

`ContextSnapshot.to_run_state_patch()` maps a verified snapshot into Phase 2 fields: current repository SHA, repository identity/remote/branch/worktree, rollback SHA supplied by the caller, and `operational_context` identity fields plus `resolution_status = RESOLVED`. It includes the GitHub authority source and credential references when present.

The projection contains no verification object and no authoritative PASS field. Context verification is not execution verification. The test suite validates the projection against `schemas/gacm-run-state.schema.json`.

## Caller responsibilities and security boundary

Callers must provide the requested operation, required-field list, expected identity constraints, Phase 3 authority result, and candidates with preserved provenance. They must persist the raw inputs and snapshot evidence durably and must not let a model rewrite the candidate or snapshot.

The resolver is deterministic and uses Git object identity checks. It does not authenticate the writer of the Phase 3 result, provide append-only persistence, calculate dependency blast radius, or issue PASS. Those remain later runtime controls owned by ORCHESTRATION, DURABLE AUTHORITY, EXECUTION / GCU, and INDEPENDENT VERIFICATION as assigned by Phase 1.
