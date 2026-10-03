# GACM Graph Foundation 06 — Hosted Staging Authority v1

**Status:** AUTHORIZED — OPENAI HOSTED CRIT REPAIR / CREDENTIAL PENDING
**Authorized:** 2026-10-03
**Provider authority resolved:** 2026-10-03
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

Human authority subsequently authorized Railway staging in workspace `chriskulbaba2025's Projects`, creation of a new dedicated GACM qualification staging project/environment, and the required staging resource cost. Railway rejected the originally proposed project name because it exceeded the provider's 32-character name limit. Human authority explicitly approved the Railway-compatible project name `gacm-qualification-sandbox-stg` and instructed execution to continue.

This authorization is staging-only. It does not authorize merge to either `main`, production mutation, reuse of an unrelated provider project, retrieval, convergence, graph-aware CRIT, legacy-planner removal, or any provider/model substitution unrelated to staging.

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

This discovery did not authorize Railway by itself.

## Resolved Railway staging authority

The following identities are now authoritative for Foundation 06 staging:

- provider: `Railway`;
- authenticated Railway principal: `chriskulbaba2025` through the connected Railway OAuth integration;
- workspace: `7ba8db0e-2024-4d68-ad54-8781fba5dd6e` — `chriskulbaba2025's Projects`;
- project: `bfff14c9-125f-483f-a3ef-a9bfba855774` — `gacm-qualification-sandbox-stg`;
- environment: `3bd45723-a62f-49ab-946c-7963553aa7ff` — `staging`;
- service: `21a38625-76eb-46ba-9333-996e867fd136` — `gacm-qualification-app`;
- persistent volume: `4d0b61fa-afa5-49aa-8f5c-63de9727e5a0` — `gacm-staging-data`;
- volume mount: `/data`;
- volume size: `512 MB`;
- source repository: `chriskulbaba2025/gacm-qualification-sandbox`;
- source branch: `candidate/foundation06-hosted-staging-20261003`;
- Foundation 05 application parent SHA: `19028a49b89a00be718ee017149a7615e966e4fd`;
- Foundation 06 hosted-identity repair candidate SHA: `7341b9c89869528eeafc2704984dbe9115d2dabc`;
- build system: Railway Railpack;
- runtime version pin: Python `3.12`;
- staging resource limits: `0.5 vCPU`, `500 MB` memory;
- restart policy: `ON_FAILURE`, maximum 3 retries;
- application data path: `/data/decisions.sqlite3`;
- graph data path: `/data/graphs/`;
- health check: `GET /`, 30-second timeout.

Credential provenance is the connected Railway OAuth integration for the authorized Railway principal/workspace. No Railway access token, provider secret, GitHub token, or other credential is committed to either repository.

The Railway source must remain pinned to an exact source SHA and must not follow future branch movement.

The first Railway deployment, `0ab21434-8a7c-44c1-a024-601d948bc089`, reached provider status `SUCCESS` at Foundation 05 app SHA `19028a49b89a00be718ee017149a7615e966e4fd`. Hosted API and governed graph behavior were functional, but Foundation 06 acceptance remained HOLD because the runtime image had no `.git` metadata, causing `application_identity.git_head=UNAVAILABLE`, and the app source-tree digest was not cross-platform stable because raw CRLF/LF bytes were hashed.

A bounded identity-only repair changed only `app.py` and `tests/test_browser.py`. It canonicalizes text line endings for source-tree identity, uses Railway-provided `RAILWAY_GIT_COMMIT_SHA` when repository metadata is unavailable, and fails closed if that runtime identity does not match `GACM_RUNTIME_EXPECTED_SHA`. It does not alter graph logic, SQLite authority, CRIT semantics, model/provider selection, or user-facing workflow behavior.

Repair evidence:

- targeted identity/browser/Phase16 tests: 34/34 PASS;
- complete application regression: 128/128 PASS;
- exact-SHA application CI: PASS at `7341b9c89869528eeafc2704984dbe9115d2dabc`;
- changed files: `app.py`, `tests/test_browser.py` only.

The staging URL is `https://gacm-qualification-app-staging.up.railway.app`. It must resolve to the accepted Railway deployment identity, and deployment metadata plus served runtime identity must both bind to source commit `7341b9c89869528eeafc2704984dbe9115d2dabc`.

The initial rollback target is `EMPTY_STAGING_TARGET` because no prior GACM staging deployment exists in this project. If the initial deployment fails acceptance, the failed deployment must not be treated as current/settled; the dedicated staging project/service/volume remain isolated while repair or teardown is separately governed.

The Railway environment patch was reviewed before commit and reported `destructive=false`. It contains only the authorized service source/configuration, two non-secret configuration variables, and the new persistent volume.

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

## Hosted staging acceptance result

Railway deployment `160f13f2-b1ae-401b-b0e2-2365d3a827e0` reached terminal `SUCCESS` for exact app SHA `7341b9c89869528eeafc2704984dbe9115d2dabc`.

Accepted hosted evidence:

- Railway deployment metadata commit SHA = `7341b9c89869528eeafc2704984dbe9115d2dabc`;
- served runtime `application_identity.git_head` = `7341b9c89869528eeafc2704984dbe9115d2dabc`;
- served runtime mode = `railway_git`;
- canonical source-tree SHA-256 = `720de64ed63db28460b96d89373b05871d92749070641f412e28cef422267f7a` locally and hosted;
- governed graph engine authority SHA = `4ecc2ead93f185bb563b99ca87580c0d90a69e27`;
- hosted root HTTP = 200;
- governed graph API = PASS;
- pre-repair idea persisted through redeploy;
- new hosted acceptance idea persisted;
- graph revisions survived provider restart exactly;
- same accepted deployment returned online after provider restart with one running replica and zero crashes/warnings;
- real Microsoft Edge hosted browser render PASS;
- browser graph revision/audit, `CLOSE_EVIDENCE_GAP`, `HUMAN_APPROVAL`, and engine SHA visible;
- browser request-failure text absent;
- staging domain: `https://gacm-qualification-app-staging.up.railway.app`;
- persistent volume remained attached at `/data`;
- production/main mutation = none.

Hosted CRIT semantic review is not accepted.

The deployed application currently instantiates `CodexCliSemanticReviewer`. The local accepted path relies on an authenticated workstation Codex CLI session. Railway does not possess that local CLI/session authority. Hosted interview evidence therefore reports:

- `question_status=REVIEW_UNAVAILABLE`;
- `current_question=null`;
- `fast_filter_status=UNAVAILABLE`;
- qualification record remains available and fail-closed.

This is correct fail-closed behavior, but it means the hosted application is not yet usable for end-to-end Human CRIT interviewing.

Foundation 06 therefore remained HOLD at end-to-end hosted acceptance until explicit hosted semantic-review authority was supplied.

## Hosted CRIT semantic-review authority

On 2026-10-03, human authority explicitly authorized:

- provider: OpenAI API, direct;
- model: `gpt-6-luna`;
- scope: Foundation 06 Railway staging only;
- credential: a dedicated OpenAI API credential;
- credential storage: Railway secret only;
- provider API: OpenAI Responses API;
- response contract: strict JSON-schema structured output;
- OpenAI tools: none;
- response persistence: disabled (`store=false`);
- CRIT authority: advisory semantic review only; GACM retains readiness, persistence, approval, graph, and release authority.

The authorized Railway configuration selector is `GACM_CRIT_PROVIDER=openai_api`. The authorized hosted model configuration is `OPENAI_CRIT_MODEL=gpt-6-luna`. The dedicated credential is referenced only as `OPENAI_API_KEY` and must never be committed, copied into governance artifacts, logs, test fixtures, or chat transcripts.

The local workstation Codex CLI path remains the default local development path when `GACM_CRIT_PROVIDER` is absent. The hosted OpenAI API path must never be selected from ambient credentials or provider availability. Unknown provider selectors must fail closed rather than falling back.

No live OpenAI API call is authorized until the dedicated credential is installed as a Railway secret. The repair may be implemented and tested with mocked provider responses before that credential is supplied.

This authorization does not change Jev's advisory-only boundary and does not authorize retrieval, web search, external tools, autonomous execution, provider/model fallback, model escalation, production deployment, or either `main` merge.

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

## Current execution gate

`READY — OPENAI HOSTED CRIT REPAIR AUTHORIZED / DEDICATED CREDENTIAL PENDING`

Railway hosting remains accepted. OpenAI API with `gpt-6-luna` is now the explicit hosted CRIT semantic-review authority for staging only. The next authorized work is the bounded provider-adapter/configuration repair with mock/no-secret tests. Live provider acceptance remains fail-closed until the dedicated `OPENAI_API_KEY` is installed directly as a Railway secret.
