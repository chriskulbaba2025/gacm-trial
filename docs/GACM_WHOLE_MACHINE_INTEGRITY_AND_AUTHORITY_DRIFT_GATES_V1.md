# GACM Whole-Machine Integrity and Instruction/Authority Drift Gates v1

## Status

This is cumulative mandatory governance for every future Foundation, repair tranche, qualification tranche, governance acceptance, staging qualification, and release candidate where applicable. It becomes mandatory starting with F15 and does not retroactively reopen F14.

Gate IDs:

- `GACM-WHOLE-MACHINE-INTEGRITY-GATE`
- `GACM-INSTRUCTION-AND-AUTHORITY-DRIFT-GATE`
- `GACM-FOUNDATION-PROGRESSION-AND-ACCEPTANCE-SYNCHRONIZATION-GATE`

Machine enforcement is owned by `src/gacm/governance/gates.py`.

## Frozen boundary

Every tranche must record the exact application and governance starting SHAs, repositories, active Foundation/tranche, authorized and prohibited changes, and expected end state. A missing or contradictory field is HOLD before consequential execution.

## Whole-machine integrity

The gate consumes identity-bound observations for every required boundary and connection. A boundary is qualifying only when its observation is `PASS`, runtime-observed, candidate-bound, receipt-bound, non-synthetic, and not caller-asserted. The cumulative evidence must also prove:

- prior accepted capabilities remain PASS;
- all required interfaces/connections remain PASS;
- regression is executed against the exact candidate;
- currentness and protected surfaces are proven;
- independent verification derives from runtime evidence and does not trust executor PASS claims;
- executor evidence remains non-authoritative.

Missing, synthetic, stale, static, callback-only, caller-asserted, or mismatched evidence produces HOLD.

## Instruction and authority drift

The gate requires an explicit row for every field in the frozen authority ledger: application/governance identities, specification, Foundation, repositories/branches, source-of-truth files, execution contracts, vendored authority, schemas, provider/model/credential/external authority, surfaces, production restrictions, approvals, repair limits, acceptance/proof requirements, verifier requirements, currentness, and prior acceptance identity.

Equal values require explicit `NO_DRIFT`. Changed values must carry one of the approved classifications. `STALE_DEPENDENCY`, `UNAUTHORIZED_CHANGE`, `MISSING_AUTHORITY`, `CONTRADICTION`, and `UNKNOWN` are blocking classifications. The gate never infers authority from environment state, installed software, credentials, defaults, prior conversation, or available providers/models.

## Acceptance and transition ordering

`acceptance_readiness` requires all three gates PASS, an exact candidate, and an acceptance-pending state. The progression gate additionally requires one authoritative candidate, exact qualification/acceptance SHA binding, currentness, and no post-qualification mutation. A next Foundation cannot begin unless the previous acceptance is already `ACCEPTED` and its exact application/governance pair matches the frozen start. A pending acceptance, supersession, second candidate, or post-qualification identity change is HOLD.

## Required evidence

The acceptance checklist must include the pre-tranche drift ledger, targeted qualification, whole-machine evidence, post-tranche drift ledger, exact-candidate currentness, independent acceptance, and frozen next-pair record. The next Foundation must not be opened from an unaccepted or unpushed candidate.
