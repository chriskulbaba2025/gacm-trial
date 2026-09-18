# GACM Pilot Harness v1

Phase 15 integrates the finite Qualification Graph into the existing governed lifecycle. The harness remains orchestration-only: GitHub authority, operational context, qualification completeness, repair scope, independent verification, promotion/rollback, and SETTLE keep their existing ownership boundaries.

## Governing lifecycle

`INITIALIZED → AUTHORITY_RESOLVED → CONTEXT_RESOLVED → PLANNED → QUALIFYING → PROMOTION_READY → PROMOTION_PENDING → SETTLE_REQUIRED → SETTLING → COMPLETED`.

The former per-work-unit `execute → verify → repair → reverify` loop is no longer the governing qualification path.

`QUALIFYING` delegates to one `QualificationCoordinator`:

`Frozen SPEC → graph compile → independent completeness PASS → graph freeze → complete safe discovery → invariant-class repair → transitive closure retest → fixed-budget escape scan → final graph replay → full regression/runtime checks → independent final verification`.

Promotion is unreachable unless that coordinator produces `pre_promotion.ready = true`. Completion is unreachable until SETTLE succeeds and the final qualification termination gate is complete.

## Resume and identity

Durable state preserves the frozen SPEC digest, graph digest, denominator, completeness evidence, discovery observations, defect classes, repair closures, escape-scan budget/results, final observations, progress, and termination state.

Resume fails closed when repository authority, frozen SPEC digest, graph digest, or denominator differs from the durable run. The graph is never silently recompiled under an existing run identity.

## Discovery and repair

Ordinary product divergence stops mutation but not safe discovery. All safely executable graph nodes are observed before ordinary repair begins. Failures are clustered by invariant/root-cause class, not test row. Repairs rerun only their proven transitive graph closure unless existing dependency evidence requires broader requalification.

## Termination

Before graph freeze, completion percentage is `UNAVAILABLE`.

After graph freeze, discovery coverage, defect closure, and final qualification coverage are reported separately. Qualification cannot self-extend after its explicit terminal conditions pass; reopening requires actual new evidence or formal human authorization.
