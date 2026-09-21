# GACM Defect and Escape Taxonomy v1

## FIXTURE_TARGET_COLLAPSE

A repair or acceptance process mistakenly treats one named failing example as the product definition of done, allowing fixture-specific success to masquerade as generalized system readiness.

Mandatory adversarial checks include: reference-only testing, a fresh scenario reusing the reference ID, fixture-token leakage into runtime code, a changed acceptance-boundary digest, and a claimed PASS without independent generalized evidence.

## SEQUENTIAL_BLOCKER_TUNNELING

A process repairs one surfaced blocker at a time without auditing the connected system first, causing repeated rediscovery of defects already inside the original capability boundary.

Mandatory adversarial checks include: missing connected-system map, narrowed scope after a new defect is found, unresolved defects inside the frozen authorized capability, and promotion attempts without whole-scope closure.

Both escape classes are permanent GACM governance defects and must remain in future adversarial audit suites.
