# GACM Graph Foundation 06 — Hosted Staging Authority v1

**Status:** AUTHORIZED / HOLD — PROVIDER IDENTITY UNRESOLVED
**Authorized:** 2026-10-03
**Production authority:** NOT GRANTED

## Purpose

Establish a separately governed hosted staging boundary for the accepted Foundation 05 qualification application without inferring provider, account, project, environment, credential, domain, deployment target, or release identity from ambient tools or accessible accounts.

## Parent authorities

GACM governance parent:

`74b08065f138159f6e1d49841b7baf0e9e6fc534`

Qualification application parent:

`19028a49b89a00be718ee017149a7615e966e4fd`

Application repository:

`chriskulbaba2025/gacm-qualification-sandbox`

Foundation 06 branches:

- governance: `governance/gacm-graph-foundation-06-hosted-staging-20261003`
- application: `candidate/foundation06-hosted-staging-20261003`

## Human authorization

On 2026-10-03, after Foundation 05 passed at its tranche boundary, human authority instructed GACM to take the next action.

This authorizes opening the hosted-staging tranche and resolving its required authority inputs.

It does not authorize GACM to choose a hosting provider, incur provider cost, create a cloud project, deploy, merge either `main`, mutate production, or reuse an unrelated provider project.

## Mandatory authority before deployment

Deployment remains fail-closed until all of the following are explicit and mutually consistent:

1. hosting provider;
2. provider account/workspace/team identity;
3. provider project identity;
4. staging environment identity;
5. credential provenance and permitted credential reference;
6. deployment target/service identity;
7. durable-storage identity required by the application;
8. staging URL/currentness contract;
9. exact candidate-to-deployment identity contract;
10. rollback target and rollback mechanism;
11. hosted browser acceptance contract.

Internal consistency is not authority.

Accessible tools, accounts, projects, credentials, domains, prior deployments, provider compatibility, convenience, or price cannot fill a missing authority field.

## Read-only discovery performed

Read-only discovery on 2026-10-03 found:

### Vercel

Accessible team:

`team_QupWFSpz8cNhhY8OAySLXC6e` — `ChrisKulbaba's projects`

No Vercel project was found by:

- project search for `gacm`;
- repository filter `chriskulbaba2025/gacm-qualification-sandbox`.

This is discovery only and does not authorize Vercel.

### Railway

Accessible workspace:

`7ba8db0e-2024-4d68-ad54-8781fba5dd6e` — `chriskulbaba2025's Projects`

No Railway project is named for GACM or `gacm-qualification-sandbox`.

An older Railway project exists:

`0a2f870a-5ca1-44b2-887d-f689a082d74d` — `spec-app`

Read-only inspection shows it contains only a `Postgres` service in its `production` environment. It does not establish authority for the Foundation 06 qualification application and must not be reused by inference.

This is discovery only and does not authorize Railway.

## Application constraints preserved

Foundation 06 must preserve the accepted Foundation 05 runtime unless a separately authorized repair is required for the selected staging provider.

Current accepted runtime characteristics include:

- Python 3.12 standard library;
- `http.server`;
- SQLite application authority;
- durable graph JSON files;
- no third-party runtime package manager;
- exact vendored GACM engine authority;
- browser-visible bounded graph state;
- fail-closed graph runtime behavior.

A provider choice that requires changing persistence, runtime architecture, authority semantics, or application behavior creates a separate material change boundary and cannot be silently absorbed into deployment work.

## Required acceptance

Before Foundation 06 may PASS:

- exact candidate local and remote identity must match;
- provider/account/project/environment authority must be recorded;
- deployment configuration must be explicit and reviewable;
- credentials must be referenced without being committed;
- deployment must produce a provider deployment identity;
- served runtime must prove the exact accepted candidate;
- durable SQLite and graph continuity must be proven across process restart/redeploy as applicable;
- real hosted browser acceptance must pass;
- graph tamper/HOLD behavior must remain fail-closed;
- application regression must remain PASS;
- deployment alias/URL must resolve to the accepted deployment;
- rollback must be proven or explicitly held if provider constraints make it unobservable;
- production must remain untouched.

## Explicit exclusions

Foundation 06 does not authorize:

- retrieval;
- graph-aware CRIT;
- convergence/shared-root detection;
- legacy-planner removal;
- cross-project learning;
- application `main` merge;
- GACM `main` merge;
- production deployment;
- production promotion;
- provider/model changes unrelated to staging;
- paid resource creation without explicit provider/account/environment authority.

## Current stop condition

`HOLD — HOSTING_PROVIDER_AUTHORITY_MISSING`

The next mutation is forbidden until human authority identifies the hosting provider and the intended provider account/workspace/team and staging project/environment boundary.
