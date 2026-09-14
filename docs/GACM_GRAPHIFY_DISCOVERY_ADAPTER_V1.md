# GACM Pilot v1 — Graphify Discovery Adapter Contract

**Phase:** 4 — Graphify Discovery Adapter
**Module:** `src/gacm/discovery/graphify_adapter.py`
**Invariant:** `Graphify discovers. GitHub proves. GACM governs.`

## Role of Graphify

The adapter isolates Graphify-specific execution behind a small configured command boundary. It sends a query and workspace to Graphify, validates the returned candidate shape, attaches concrete workspace provenance, and classifies discovery as `DISCOVERED`, `NO_MATCH`, `AMBIGUOUS`, or `ERROR`.

Graphify is a discovery/index layer only. It may locate relationships and candidate sources; it cannot authorize a repository, branch, account, tenant, environment, deployment target, execution permission, or PASS. The adapter never returns `VERIFIED` and never emits an authoritative verification decision.

## Supported discovery query classes

The query is caller-supplied. The adapter supports the following relationship classes without hard-coding their source or target values:

- project → repository
- repository → config
- config → environment
- environment → account
- service → deployment target
- code module → dependency
- code module → impacted files
- requirement → implementation surface
- SOP → governed operation
- schema → dependent code
- documentation → referenced configuration

Graphify may return additional relationship labels, but every returned candidate must satisfy the same provenance and source-path rules.

## Configuration and execution

`GraphifyConfig` requires:

- `command` — executable plus arguments, supplied by the caller;
- `repository_path` — the workspace passed as subprocess working directory and provenance;
- `query` — the exact requested relationship query;
- `max_results` — hard upper bound;
- `timeout_seconds` — subprocess timeout;
- optional `repository_identity` — caller-provided identity used for candidate consistency checks.

The adapter sends JSON on standard input:

```json
{
  "query": "...",
  "repository_path": "...",
  "max_results": 20
}
```

No local path, repository, executable, or network endpoint is hard-coded. If the executable is unavailable, times out, exits non-zero, or emits invalid JSON, the adapter returns deterministic `ERROR`. It does not fall back to model reasoning or filesystem guessing.

## Candidate provenance

Every accepted candidate must include:

- `source_path` — safe relative path, with no absolute path or traversal;
- `source_type` — such as `config`, `code`, `schema`, or `documentation`;
- `relationship` — the discovered relationship label;
- `target` — the relationship target;
- `confidence` — numeric value in `[0, 1]`;
- `query` — exact equality with the requested query.

The adapter adds the resolved workspace path and preserves the configured repository identity where available. A candidate with missing provenance, mismatched query, unsafe source path, invalid confidence, or conflicting repository identity is rejected as `ERROR` for the whole discovery result. This prevents partially trusted output from entering a governed path.

Graphify may include `source_revision`; the adapter preserves it as discovery metadata. It is not treated as the authoritative Git revision until the Phase 3 resolver and handoff check prove the source in the governed Git state.

## Discovery states

| State | Meaning | May authorize execution? |
|---|---|---|
| `DISCOVERED` | Exactly one structurally valid candidate was returned. | No. |
| `NO_MATCH` | Graphify returned zero candidates. | No. |
| `AMBIGUOUS` | More than one structurally valid candidate was returned, or the caller cannot uniquely select one. | No. |
| `ERROR` | Graphify unavailable, timed out, failed, emitted malformed output, or returned untraceable data. | No. |

`ACCEPTED_FOR_AUTHORITY_RESOLUTION` is used only by the separate handoff result after source-presence proof. It is deliberately not a Graphify discovery state and is not `VERIFIED`.

## GitHub authority handoff

For a candidate that may affect execution:

1. Graphify returns the candidate and its query/source provenance.
2. The adapter validates structural provenance and rejects unsafe/untraceable candidates.
3. The Phase 3 GitHub Authority Resolver must return `VERIFIED` for the intended repository, branch/ref, local HEAD, remote HEAD, clean worktree, and required authority files.
4. `handoff_candidates()` proves the candidate `source_path` exists in that exact verified Git HEAD using `git cat-file` and records the source blob SHA.
5. The handoff returns `ACCEPTED_FOR_AUTHORITY_RESOLUTION`, not authority and not operational context.
6. A later Phase 5 context layer may decide whether the source content supports a governed fact.

If the authority result is `BLOCKED` or `AMBIGUOUS`, or the source is absent from the verified Git HEAD, the handoff returns `REJECTED`. A candidate cannot override a GitHub result, and a candidate present in GitHub is still only a source candidate until a later authority-context layer interprets it.

## Ambiguity and failure handling

Multiple candidates are returned as `AMBIGUOUS`; the adapter does not choose the highest confidence candidate. A caller may issue a narrower query or invoke a later governed disambiguation step. `NO_MATCH` is not permission to invent a source. `ERROR` is not permission to use stale Graphify data, chat memory, or model guesses.

The adapter does not silently truncate candidates beyond `max_results`; it returns `ERROR`. This preserves the distinction between a bounded result and an incomplete result set.

## Phase 2 durable state recording

`discovery_evidence()` creates a Phase 2-compatible evidence record with a content digest, `kind = graphify-discovery`, and `produced_by = ORCHESTRATION`. The raw discovery result remains the evidence payload addressed by that digest. Recording the evidence does not modify `operational_context`, repository identity, branch, environment, or verification status.

The Phase 2 run-state record can therefore preserve what Graphify found without turning the finding into authority. A run-state consumer must treat the evidence as discovery input and require a separate GitHub handoff plus later context resolution before using it for execution.

## Caller responsibilities

Callers must:

- supply the intended workspace, executable, query, result bound, and timeout;
- preserve the raw result and its evidence digest durably;
- treat every non-`DISCOVERED` result as non-authorizing;
- invoke the Phase 3 resolver before relying on a material candidate;
- handle `AMBIGUOUS`, `NO_MATCH`, `ERROR`, and rejected handoff states fail-closed;
- prevent an executor or model from rewriting candidate provenance or selecting authority;
- pass accepted source candidates to the later operational-context layer, not directly to execution.

## Security boundary

Graphify output is untrusted input. The adapter uses a no-shell subprocess call, a configured timeout, a result bound, strict JSON shape checks, safe relative paths, exact query matching, and repository identity consistency checks. It does not execute candidate paths, read arbitrary candidate content for interpretation, or pass Graphify output directly to a provider or deployment target.

The GitHub handoff checks source presence and Git object identity only. It does not assert that the source content is semantically correct, that a configuration is safe, or that a deployment/account mapping is authorized.

## Support for later operational-context resolution

The adapter supplies the later context layer with candidate source paths, relationship labels, targets, query provenance, workspace/repository identity, verified Git HEAD, and source blob SHA. The context layer must then resolve the candidate’s material values against authoritative durable state and produce exactly one context or stop with an ambiguity/missing-authority result. This Phase 4 adapter does not implement that resolver.
