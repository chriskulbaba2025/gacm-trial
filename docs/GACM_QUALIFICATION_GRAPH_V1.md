# GACM Qualification Graph and Finite Qualification Contract v1

**Phase:** 15 methodology correction  
**Scope:** qualification planning, discovery, repair batching, escape scan, termination  
**Authority preserved:** frozen SPEC remains unchanged; Graphify remains discovery-only; GitHub/durable evidence remains authority.

## Root defect

The Phase 13 pilot harness executes, verifies, repairs, and re-verifies inside one work-unit loop. That is safe but serializes discovery. A normal product divergence therefore hides later ordinary divergences until the first repair cycle completes.

The correction is to separate **discovery** from **mutation** and to establish a finite qualification denominator before execution.

## Required sequence

```text
Frozen SPEC
→ Qualification Graph compile
→ independent completeness verification
→ graph freeze
→ sandbox-safe complete discovery sweep
→ invariant-class defect clustering
→ one bounded defect-class repair at a time
→ affected transitive closure retest
→ bounded adversarial escape scan
→ full qualification / regression / runtime verification
→ independent final verification
→ SETTLE
```

No extra qualification stage is created after those terminal conditions succeed unless new evidence formally reopens governance.

## Qualification Graph

Every normative frozen SPEC requirement MUST map to at least one node. Every node MUST map to exactly one frozen SPEC requirement. A graph with an unmapped requirement or a foreign node cannot freeze.

Every node records:

- SPEC requirement ID
- invariant
- affected surface
- prerequisites/dependencies
- fixture/input
- oracle
- expected result
- mutation risk
- failure class
- discovery continuation policy
- repair class
- transitive retest closure
- required evidence
- final verification method

The graph also records the frozen SPEC digest, an independent completeness verifier identity, completeness evidence, and a deterministic graph digest.

After freeze, the node denominator is immutable. Changing it requires formal governance reopen, not an in-run edit.

## Discovery rule

Ordinary product divergences stop mutation, not discovery.

The discovery sweep is read-only/sandbox-safe with respect to governed product state. It records PASS, FAIL, BLOCKED, or HUMAN_DEFERRED for each safe node and continues after ordinary FAIL/BLOCKED observations.

Discovery hard-stops only for unsafe conditions, including authority violation, unexpected external/shared-state mutation, production access, destructive corruption, credential/security exposure, verifier compromise, or other unsafe execution.

No repair occurs inside the discovery sweep.

## Repair rule

After the sweep, FAIL nodes are clustered by violated invariant. The repair unit is the invariant/root-cause class, not an individual test row.

A bounded repair may modify only its authorized surface. Retest scope is the repaired nodes plus their proven transitive retest closure. Existing Phase 9 dependency logic remains authoritative for broader scope/assurance invalidation when code surfaces require it.

Full regression and independent final verification are final-gate activities rather than mandatory after every small repair.

## Bounded adversarial escape scan

The escape scan has a fixed budget recorded before it begins. Executed cases cannot exceed the budget and the scan cannot enlarge its own budget.

Its purpose is to find material omissions outside deterministic SPEC assumptions: cross-feature interaction, unexpected sequence, stale/malformed state, runtime/browser divergence, or an obvious omitted edge condition.

A genuine escaped defect reopens only the affected invariant closure. Merely imagining another possible test does not reopen qualification.

## Progress

Before graph freeze:

```text
Completion percentage = UNAVAILABLE
```

After graph freeze, report three separate measures:

- Discovery coverage = terminal discovery observations / frozen node denominator
- Defect closure = closed-or-human-deferred invariant classes / discovered invariant classes
- Final qualification coverage = terminal final nodes / frozen node denominator

Do not combine these into an intuitive overall percentage.

## Termination

Phase qualification is complete only when all of these are true:

1. Graph completeness is proven with zero unmapped frozen SPEC requirements.
2. Every graph node has a terminal disposition.
3. Every discovered defect class is closed or explicitly human-deferred.
4. The bounded adversarial escape scan is complete with no unresolved escaped defect.
5. Full regression is green.
6. Required real runtime/browser checks are green.
7. Independent final verification is green.
8. SETTLE succeeds.

After this, GACM MUST NOT create another cleanup stage, qualification layer, or open-ended test pass simply because another hypothetical case can be imagined.

Reopen requires actual new evidence: escaped defect, changed requirement, security finding, dependency/runtime change, contradictory evidence, or formal human reopen authorization.

## Implementation

The executable contract is `src/gacm/qualification/graph.py`.

It intentionally does not mutate the Phase 15 sandbox and does not add Stage F Test 07. It provides:

- deterministic graph compilation and completeness checks;
- immutable denominator and graph digest;
- safe complete discovery behavior;
- invariant clustering;
- transitive retest closure;
- bounded escape-scan contract;
- progress semantics;
- explicit termination evaluation.

The existing PilotHarness is not silently changed in this correction. Phase 15 qualification must enter the graph path before further Stage F execution; the old per-unit repair loop is no longer the governing qualification process for this phase.
