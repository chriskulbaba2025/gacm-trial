# GACM Foundation Acceptance Checklist v1

For each Foundation N, record one exact candidate and one exact governance acceptance identity.

## Before execution

- [ ] Starting application SHA and repository match the frozen previous pair.
- [ ] Starting governance SHA and repository match the frozen previous pair.
- [ ] Previous acceptance status is `ACCEPTED`.
- [ ] Active Foundation/tranche, authorized change, prohibited change, and expected end state are explicit.
- [ ] All 27 instruction/authority drift fields have an explicit ledger row.
- [ ] No blocking drift class exists.

## Qualification

- [ ] Foundation-specific targeted qualification passes.
- [ ] Required real runtime boundaries are runtime-observed, non-synthetic, and candidate-bound.
- [ ] Every material connection between accepted layers is runtime-observed and candidate-bound.
- [ ] Previously accepted capabilities remain PASS.
- [ ] Whole-machine regression passes on the exact candidate.
- [ ] Independent verification does not trust executor PASS claims.

## Close

- [ ] Post-tranche drift ledger has no blocking class.
- [ ] Application and governance local heads equal their remote candidate heads.
- [ ] Main branches and production satisfy their protected-state assertions.
- [ ] Governance acceptance records the whole-machine result and both gate receipts.
- [ ] New application/governance pair is frozen before the next Foundation begins.
