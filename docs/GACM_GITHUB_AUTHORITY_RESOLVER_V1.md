# GACM Pilot v1 — GitHub Authority Resolver Contract

**Phase:** 3 — GitHub Authority Resolver
**Module:** `src/gacm/authority/resolver.py`
**CLI:** `python -m gacm.authority` with `PYTHONPATH=src`

## Purpose

The resolver establishes the repository state that may authorize a later governed step. It accepts a configured worktree, intended branch/ref, remote, required authority files, and optional expected repository/authorized-head identities. It returns machine-readable `VERIFIED`, `BLOCKED`, or `AMBIGUOUS` JSON.

The resolver is deliberately smaller than orchestration. It does not retrieve operational account/tenant context, invoke Graphify, choose a model, execute work, or issue verification PASS.

## What is authoritative

For this boundary, Git and the configured remote are authoritative:

- repository identity comes from the configured remote URL;
- local branch and local HEAD come from Git in the checked-out worktree;
- remote branch HEAD comes from an exact `git ls-remote` lookup of the configured ref;
- ancestry/divergence comes from Git’s `merge-base --is-ancestor` after the exact remote ref is fetched into the local object database;
- worktree cleanliness comes from `git status --porcelain --untracked-files=all`;
- authority-file existence comes from the configured repository path;
- PRD content identity for run-state projection comes from `git hash-object`.

The resolver does not treat chat, model memory, harness memory, Graphify, filenames supplied by a model, or a prior JSON result as authority.

## Inputs and caller contract

`ResolverConfig` requires:

- `repository_path` — the intended checked-out worktree;
- `intended_branch` — the exact governed local branch;
- `remote_name` — normally `origin`;
- optional exact `intended_ref` — otherwise `refs/heads/<intended_branch>`;
- optional `expected_repository` — normalized identity such as `owner/repository`;
- optional `authorized_head` — exact remote SHA required by the caller;
- required authority files, defaulting to `CURRENT_STATE.md` and `GACM_IMPLEMENTATION_PRD_V1.0.md`;
- `protected_rollback_sha` only when projecting into the Phase 2 run-state schema.

Callers must obtain the intended branch/ref and authorized SHA from their own approved durable configuration. The resolver does not infer a branch, substitute a default project, or ask a model to choose among candidates. If a caller omits `authorized_head`, the current exact remote branch HEAD is the remote authority for this check; callers that require a pre-approved candidate must supply the SHA explicitly.

## Result states

### `VERIFIED`

Returned only when all of the following are true:

- repository path and Git repository are usable;
- remote identity is established and matches `expected_repository` when supplied;
- current branch equals `intended_branch`;
- local HEAD is a full SHA;
- all required authority files exist;
- worktree is clean;
- exact remote ref resolves to one SHA;
- remote SHA matches `authorized_head` when supplied;
- local and remote HEAD are equal;
- divergence is `MATCH`.

### `BLOCKED`

Returned for any deterministic blocking condition:

- required authority file is missing;
- local HEAD differs from required authorized HEAD;
- local and remote HEAD differ (`AHEAD`, `BEHIND`, or `DIVERGED`);
- worktree is dirty;
- current branch is not the intended branch;
- repository identity mismatches the expected identity;
- Git cannot establish repository, branch, HEAD, worktree, remote, or ancestry state;
- exact remote ref is ambiguous and another blocking condition also exists.

Blocking reasons are structured strings in `blocking_reasons`. No execution model may remove, reinterpret, or override them.

### `AMBIGUOUS`

Returned when the exact remote ref has no uniquely resolvable SHA and no other deterministic blocking reason was found. The current implementation treats zero matching remote heads as unresolved ref ambiguity. Multiple matching heads are also ambiguous by contract. A caller must resolve the ref configuration or stop; it must not guess.

## Local versus remote identity

`local_head` is the commit checked out in the worktree. `remote_head` is the exact SHA returned by the configured remote/ref lookup. They are separate identities and both are required in the result. The resolver never treats a matching branch name, repository URL, or stale remote-tracking ref as proof that the commits match.

For ancestry classification, the resolver fetches the exact configured ref with `git fetch --no-tags <remote> <ref>`. This materializes objects for `merge-base`; it does not update the checked-out branch, merge code, or worktree. If materialization fails, the result is `BLOCKED` because divergence cannot be proven.

## What Git does not prove

Git alone does not prove:

- that a human approved the authorized SHA;
- that cloud account, tenant, environment, region, deployment, or credential identity is correct;
- that a Graphify relationship is authoritative;
- that a PRD is semantically acceptable;
- that code is safe, verified, deployed, or settled;
- that a writer is authorized to alter durable run state;
- that the result has been persisted append-only or replay-protected.

Those responsibilities remain with the Phase 1 ownership map and later GACM layers. This resolver only supplies repository authority evidence.

## Fail-closed rules

The resolver never returns `VERIFIED` on partial evidence. It does not:

- fall back to the current branch when the intended branch is absent;
- use a local SHA when remote resolution fails;
- accept a dirty worktree because the dirty files look harmless;
- accept a local-ahead or remote-ahead worktree as equivalent;
- substitute a repository identity from a model or path name;
- treat an unresolved remote ref as a best match;
- return a PASS-like status that an executor can reinterpret.

The CLI emits JSON only; the caller owns the non-zero process policy for blocked/ambiguous results. A future orchestration layer must make `status != VERIFIED` a no-side-effect gate.

## Phase 2 run-state integration

`ResolutionResult.to_run_state_patch()` is the narrow integration seam. It is available only for `VERIFIED` results and produces fields compatible with the Phase 2 contract:

- `current_repository_sha` from `local_head`;
- `repository.repository_id`, `remote`, `branch`, `worktree`, and caller-supplied protected rollback SHA;
- `prd.identity` and a Git content hash for `GACM_IMPLEMENTATION_PRD_V1.0.md`.

The resolver does not fabricate a rollback target. `protected_rollback_sha` is required for projection because the Phase 2 schema requires durable rollback authority. The test suite merges this patch into a representative Phase 2 run-state fixture and validates it with the canonical JSON Schema.

## CLI example

```powershell
$env:PYTHONPATH = "src"
python -m gacm.authority `
  --repo . `
  --branch main `
  --expected-repository chriskulbaba2025/gacm-trial `
  --authorized-head (git rev-parse HEAD)
```

The output includes status, repository/remote/ref identity, local and remote SHAs, cleanliness, divergence, authority-file lists, identity matches, and blocking/ambiguity reasons.

## Relationship to later phases

This module is Phase 3 only. It establishes repository authority before governed execution. It does not implement Graphify discovery, authoritative operational context resolution, model routing, GCU execution, independent verification, repair scope, promotion, rollback transitions, or SETTLE behavior.
