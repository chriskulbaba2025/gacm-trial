# GACM Red Queen and Token-Efficient Execution Process v1

**Status:** proposed governance process for review  
**Scope:** GACM governed coding tranches  
**Authority:** additive to the frozen GACM methodology; it does not authorize a new tranche, controller mutation, production action, model/provider change, or autonomous next-tranche progression.

## Purpose

GACM must improve reliability under repeated change while spending the fewest tokens and tool calls that still produce the required evidence. This document defines the operating loop and the efficiency record. It is a process contract, not a claim that the local controller already enforces every step.

## Operating invariants

1. Exact repository, branch, starting SHA, tranche, environment, model/provider, budget, allowed surfaces, retry bound, and acceptance contract are frozen before execution.
2. A model or execution agent cannot create authoritative PASS. Independent verification remains the decision authority.
3. Production is read-only unless separately authorized.
4. Missing evidence is not PASS. Preserve PASS, FAIL, HOLD, UNKNOWN, PARTIAL, UNAVAILABLE, NOT_CONNECTED, and NOT_APPLICABLE as distinct states.
5. Three failed repairs in one defect family require a diagnostic reset. Do not continue symptom patching.
6. A bounded tranche ends at its defined outcome; the Red Queen loop never silently opens the next tranche.

## Red Queen loop

The Red Queen is a recurring adversarial challenger around each governed candidate, not an autonomous decision-maker.

### Required sequence

1. **Pre-action challenge:** before a material action, challenge authority, identity, scope, model/provider, budget, retry, and production-boundary assumptions.
2. **Execute one bounded action:** every material action must have the frozen execution recipe and deterministic authorization.
3. **Verify independently:** check the expected result, exact candidate identity, scope preservation, forbidden changes, tests, proof, and runtime identity where applicable.
4. **Challenge the result:** run the smallest relevant negative-control checks against the accepted candidate.
5. **Repair only the owning boundary:** if a check fails, record root cause and blast radius, make one surgical repair, and rerun affected verification plus required dependents.
6. **Re-challenge after repair:** repeat the negative controls that cover the repaired boundary; do not rerun unrelated work without a causal reason.
7. **Close or reset:** close only on complete in-scope evidence. After three same-family failed repairs, reset diagnosis. If evidence is unavailable or identity drifts, HOLD.

### Minimum negative-control inventory

Select controls relevant to the tranche, recording setup, expected reject/hold, observed side effect, candidate SHA, and proof digest:

- untrusted repository text cannot mint approval or alter scope;
- stale SHA and source-of-truth races are rejected;
- concurrent or replayed actions cannot duplicate effects;
- expired, cross-project, or already-consumed grants are rejected;
- approved model/provider cannot be silently substituted or escalated;
- path traversal and writes outside the allowlist are rejected;
- token, tool, time, paid-provider, retry, and tranche ceilings are enforced;
- forged, empty, self-certified, or wrong-candidate proof is rejected;
- staging cannot escalate to production;
- interruption between an effect and its receipt recovers safely or reports HOLD;
- disconnected persistence/controller state cannot report success.

The challenger may reject or produce HOLD, but may not mint approval, expand scope, select a model, repair code, or certify its own result.

## Token-efficiency structure

Token efficiency is a success metric only after the evidence floor is met. The objective is **minimum sufficient work**, not minimum work at the cost of correctness.

### Required run record

For every governed run, record:

| Metric | Required meaning |
| --- | --- |
| `token_budget` | Frozen maximum available for the tranche |
| `tokens_used` | Provider-reported usage when available; otherwise `UNAVAILABLE` |
| `tool_calls` | Count of tool calls, including retries |
| `round_trips` | Count of model/tool interaction cycles |
| `wall_clock_ms` | Elapsed run time |
| `evidence_artifacts` | Proof files and their identities/digests |
| `targeted_tests` | Tests run and affected boundary |
| `broad_regression` | Required only when the acceptance contract says so |
| `repair_attempts` | Attempts by defect family |
| `reruns_avoided` | Independent checks not repeated because no causal impact existed |
| `human_interventions` | Required questions, approvals, or manual actions |
| `result` | PASS, FAIL, HOLD, or another governed state |

If a provider does not expose token counts, do not estimate or invent them. Use observable proxies and mark the metric unavailable.

### Efficiency rules

- Read the smallest authoritative slice needed to decide the next action; avoid repeated giant dumps.
- Prefer one high-information diagnostic over speculative edits.
- Reuse verified context and proof identities; do not rediscover unchanged state.
- Run targeted verification first, then the contract-required broader regression.
- Retry only for a new causal reason; identical output is a diagnostic signal, not progress.
- Stop when the acceptance contract is satisfied or a genuine blocker is established.
- Never reduce required independent, identity, security, browser, regression, or settlement evidence to save tokens.
- Never count an omitted required check as a saving.

### Efficiency acceptance

A run may report `TOKEN_EFFICIENCY: PASS` only when:

1. all required acceptance evidence is present;
2. no required check was skipped;
3. each repair and rerun has a recorded causal reason;
4. no duplicate diagnostic/tool cycle lacks new information;
5. usage is within the frozen budget, or an approved exception is recorded;
6. the exact candidate and proof identities are current.

Otherwise report `TOKEN_EFFICIENCY: HOLD` (or `FAIL` when the contract defines an explicit failure).

## Required receipt fields

A completion receipt should include:

```
RED_QUEEN_CHALLENGE: PASS | FAIL | HOLD | NOT_APPLICABLE
TOKEN_EFFICIENCY: PASS | FAIL | HOLD | UNAVAILABLE
TOKEN_EFFICIENCY_BASIS: provider counts | observable proxy | unavailable
CANDIDATE_SHA: <exact identity>
REPAIR_ATTEMPTS_BY_FAMILY: <map>
DUPLICATE_CYCLES_WITHOUT_NEW_INFORMATION: <count>
REQUIRED_CHECKS_SKIPPED: <count>
```

These fields supplement, and do not replace, the existing independent-verification, currentness, production-path-equivalence, and production-identity-continuity gates.

## Implementation boundary

This document provides an additive operating contract. It does not assert that `gacm-controller` currently enforces these controls. A future controller-boundary tranche must inspect the actual controller, map each field and negative control to an owning implementation boundary, add deterministic tests, and produce exact-candidate runtime proof before claiming enforcement.
