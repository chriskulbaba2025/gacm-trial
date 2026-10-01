# GACM Defect and Escape Taxonomy v1

## FIXTURE_TARGET_COLLAPSE

A repair or acceptance process mistakenly treats one named failing example as the product definition of done, allowing fixture-specific success to masquerade as generalized system readiness.

Mandatory adversarial checks include: reference-only testing, a fresh scenario reusing the reference ID, fixture-token leakage into runtime code, a changed acceptance-boundary digest, and a claimed PASS without independent generalized evidence.

## SEQUENTIAL_BLOCKER_TUNNELING

A process repairs one surfaced blocker at a time without auditing the connected system first, causing repeated rediscovery of defects already inside the original capability boundary.

Mandatory adversarial checks include: missing connected-system map, narrowed scope after a new defect is found, unresolved defects inside the frozen authorized capability, and promotion attempts without whole-scope closure.

Both escape classes are permanent GACM governance defects and must remain in future adversarial audit suites.

## EXTERNAL_PROVIDER_AUTHORITY_UNDER_SPECIFICATION

A governed executor selects or infers an external provider/service without an authoritative project-specific provider identity. Ambient credentials, installed SDKs, API compatibility, lower cost, provider popularity, another project's configuration, or a self-consistent runtime manifest are not authority.

Mandatory adversarial checks include: unknown provider, alternate compatible provider, matching unauthorized manifest/runtime, cheaper substitute, unavailable approved provider, stale provider configuration, and multiple discovered providers.

## CREDENTIAL_PROVENANCE_UNDER_SPECIFICATION

A governed executor uses an available credential without proving that the credential belongs to the governed project, selected provider/service, intended environment and authorized account/project/tenant scope.

Mandatory adversarial checks include: unrelated global token, wrong account/environment, wrong credential source, multiple discovered credentials, and a valid provider identity paired with unproven credential provenance.

Both failure patterns are permanent GACM governance defects. They are machine-prevented by `GACM-EXTERNAL-PROVIDER-AUTHORITY-AND-CREDENTIAL-PROVENANCE-GATE` and must remain in future governance regression suites.
