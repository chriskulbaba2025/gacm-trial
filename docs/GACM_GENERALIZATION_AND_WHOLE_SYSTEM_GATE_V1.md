# GACM Generalization and Whole-System Gate v1

## Authority

Gate ID:

`GACM-GENERALIZATION-AND-WHOLE-SYSTEM-GATE`

This is a mandatory, fail-closed governance control for governed product repair. It is machine-enforced and cannot be overridden by executor prose, test fixture success, or a claimed PASS.

## Root failure prevented

The gate prevents a product repair from collapsing into repair of one known failing fixture and prevents sequential blocker tunneling where one visible defect is repaired at a time without first mapping the connected capability.

## Pre-execution contract

Before execution begins, GACM must freeze a generalization contract containing:

- a product-level definition of done;
- the authorized capability scope;
- the connected system path;
- required full-path boundaries;
- the minimum number of fresh materially different scenarios, never less than two for variable-input products;
- reference regression IDs, explicitly marked as regression-only;
- continuity controls required by the product contract;
- security, privacy, and isolation controls required by the product contract;
- either `GENERALIZED` mode or an explicitly authorized `FIXTURE_SPECIFIC_AUTHORIZED` mode.

The harness hashes this contract before execution. A later contract digest mismatch blocks the run.

## Whole-system rule

The connected system must be mapped before repair. The map is product-specific, but may include input, parsing, normalization, governing contract, interpretation, decision logic, persistence, reconstruction/reopen, presentation/reporting, identity, isolation/security, and downstream consumers.

Discovery of a later defect does not narrow the frozen definition of done.

## Generalization acceptance

For `GENERALIZED` mode, authoritative closure requires at least two fresh materially different scenarios that are not reference fixtures. Each scenario must:

- have a distinct input identity;
- execute through the same generic runtime path identity;
- prove every required full-path boundary;
- carry durable evidence references.

Reference regression proof is separate and additional.

## Fixture-dependency control

The runtime path must have a machine-produced fixture-dependency scan. Any detected test-fixture import, reference token in runtime logic, named-case branch, frozen expected output used as runtime authority, or test-only fallback fails the gate.

## Full-path continuity

Where required by the frozen product contract, evidence must prove save/reopen, reconstruction, downstream calculations, report/output continuity, identity continuity, cross-run isolation, cross-user or tenant isolation, privacy/security controls, and full regression.

A compile pass, isolated service test, source inspection, known fixture, or executor claim cannot substitute for required full-path evidence.

## Independent evidence

Generalization evidence must be issued by the independent verifier and marked authoritative. GACM governance re-evaluates that raw evidence against the frozen contract. The executor cannot produce authoritative gate PASS.

## Fixture-specific exception

A genuinely fixture-specific work unit may use `FIXTURE_SPECIFIC_AUTHORIZED` only when the frozen contract contains durable authorization by HUMAN, GACM_GOVERNANCE, or RELEASE_AUTHORITY, including a reason and evidence ID.

Omitting the generalization contract is not an exception.

## Promotion boundary

Promotion eligibility re-runs this gate from the raw generalization contract and raw independent evidence. A claimed gate result that disagrees with the machine result is rejected.

## Required closure

Generalized product repair can close only when:

1. the product-level definition of done remained frozen;
2. the connected system was audited;
3. the owning generic boundary was repaired;
4. fresh materially different inputs passed;
5. required end-to-end continuity passed;
6. the original reference regression still passed;
7. no fixture-specific runtime dependency remains;
8. required security/privacy/isolation controls passed;
9. full regression passed;
10. evidence is durable and independently verifiable.

Any unproven item is HOLD.

## Universal runtime model

`variable valid input → generic system path → durable output → downstream continuity → generalized acceptance`

Project-specific nouns must not be embedded into the universal gate.
