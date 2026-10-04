# GACM Graph Foundation 06 — Hosted Staging Authority v1

**Status:** ACCEPTED — FOUNDATION 06 HOSTED STAGING / LIVE OPENAI CRIT
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

The bounded implementation candidate is `7da781a4e4279082c117442b52a9d70abad2a9c2`, parent `7341b9c89869528eeafc2704984dbe9115d2dabc`. It changes only `app.py`, `crit_review.py`, and `tests/test_crit_review_provider.py`. Evidence: targeted provider/local-regression tests 42/42 PASS; complete application regression 132/132 PASS; exact-SHA application CI PASS; secret scan 0; live provider calls 0.

The candidate preserves the local Codex CLI default and introduces `OpenAIResponsesSemanticReviewer` only behind explicit selector `GACM_CRIT_PROVIDER=openai_api`. It hard-binds the direct endpoint `https://api.openai.com/v1/responses`, authorizes only `gpt-6-luna`, sends `tools=[]`, sends `store=false`, uses strict JSON-schema structured output, bounds request/response sizes and timeouts, records provider response/model provenance, and fails closed on unknown provider, unauthorized model, missing credential, provider refusal, malformed output, or provider failure.

A staging deployment of this exact candidate was authorized before the credential was installed only to prove provider selection/configuration and missing-secret fail-closed behavior.

That deployment is now complete:

- Railway deployment: `62f90b69-5b92-47ac-b239-1fc49aac254f`;
- provider status: `SUCCESS`;
- Railway commit metadata: `7da781a4e4279082c117442b52a9d70abad2a9c2`;
- served runtime git identity: `7da781a4e4279082c117442b52a9d70abad2a9c2`;
- local and hosted canonical source-tree SHA-256: `dc2f59d0672c7de4a31dd2c876ebfaa532b0dcfefffcc2390d3721b85e044f50`;
- graph runtime: PASS;
- engine authority SHA: `4ecc2ead93f185bb563b99ca87580c0d90a69e27`;
- Railway variables present: `GACM_CRIT_PROVIDER`, `OPENAI_CRIT_MODEL`, `GACM_RUNTIME_EXPECTED_SHA`, `RAILPACK_PYTHON_VERSION`;
- `OPENAI_API_KEY`: absent;
- hosted interview `question_status=REVIEW_UNAVAILABLE`;
- hosted interview `current_question=null`;
- hosted fast-filter status: `UNAVAILABLE`;
- qualification record remains available;
- Railway DNS log entries for this no-secret acceptance: none;
- live OpenAI provider calls: 0.

This proved the provider selector was active, exact runtime identity was current, and the credential gate failed closed before a provider request.

## Live OpenAI CRIT acceptance

Human authority reported the dedicated API key installed directly in Railway as `OPENAI_API_KEY`. The credential value was never retrieved by GACM, never written to repository or proof artifacts, and never exposed in persisted API output.

Railway automatically created deployment `874479f2-1360-4d1f-8025-89862e11313b`, which reached terminal `SUCCESS` while remaining pinned to exact source commit `7da781a4e4279082c117442b52a9d70abad2a9c2`.

Live governed acceptance used fresh idea `idea-7d5a15bd91a84b8da1c37a6ae45b33b9`.

Observed live behavior:

- initial Human CRIT interview status: `READY`;
- Fast Filter status: `AVAILABLE`;
- Fast Filter authority: `ADVISORY_ONLY`;
- Fast Filter provenance: provider `openai_api`, requested/resolved model `gpt-6-luna`, Responses API, `tools=false`, `store=false`;
- CRIT selected a context-specific evidence question rather than a fixture-specific question;
- first answer review returned `NEEDS_FOLLOWUP` with a material gap and one neutral follow-up;
- the follow-up answer returned `RESOLVED`;
- CRIT advanced from evidence dimension `evidence_plan` to feasibility dimension `access_limits`;
- all persisted semantic-review provenance records retained `openai_api / gpt-6-luna`, response IDs, `tools=false`, and `store=false`;
- browser rendering of the live state passed in real Microsoft Edge;
- rendered UI showed the live feasibility question, resolved feedback, and persisted answer;
- rendered UI contained no `REVIEW_UNAVAILABLE` and no request-failure text;
- Railway DNS evidence showed only the authorized OpenAI endpoint `api.openai.com` for semantic-review calls;
- no credential value appeared in persisted API output or deploy logs examined during acceptance;
- exact served runtime git identity remained `7da781a4e4279082c117442b52a9d70abad2a9c2`;
- local and hosted canonical source-tree SHA-256 remained `dc2f59d0672c7de4a31dd2c876ebfaa532b0dcfefffcc2390d3721b85e044f50`;
- the idea created before credential installation remained readable after the secret-triggered redeploy, with graph status PASS and current exact application identity;
- persistent SQLite/graph continuity therefore remained intact across the final deployment transition;
- production and both `main` branches remained untouched.

Foundation 06 hosted-staging acceptance was initially recorded PASS on deployment `874479f2-1360-4d1f-8025-89862e11313b` / app SHA `7da781a4e4279082c117442b52a9d70abad2a9c2`. Additional live acceptance then exposed an intermittent answer-review validator fallback, so that earlier acceptance evidence is superseded by the repair evidence below.

## Superseding live answer-review contract repair

A stale-client `ANSWER_REVISION_MUST_BE_REQUESTED` response observed during testing was correct fail-closed behavior: the tested idea had already advanced to newer persisted answers before the stale submission arrived. It did not mutate or overwrite the newer state.

The actual defect was separate. OpenAI answer-review calls were completing successfully, but the original strict JSON schema guaranteed field shapes without encoding all GACM CRIT cross-field invariants. This allowed occasional schema-valid review objects that the downstream GACM validator correctly rejected, producing fail-closed `REVIEW_PENDING`.

The bounded diagnostic candidate `2cee8eab46a62e7ec16b8357d44b00558c8e19ff` added only a sanitized validator error-code field to fail-closed review quality. No prompt, answer, credential, raw provider response, or provider diagnostic is persisted by that field. Evidence: 40/40 targeted PASS, 133/133 full regression PASS, exact-SHA application CI PASS.

The final repair candidate `d8452cdf040d75360e711c994c2b911189d4842c` is the accepted Foundation 06 application candidate. Relative to the diagnostic candidate it changes only `crit_review.py` and `tests/test_crit_review_provider.py`.

The OpenAI-only answer-review schema now structurally enforces the same resolution-state invariants already enforced by GACM post-validation. It uses a supported nested `anyOf` shape and preserves the local Codex CLI contract unchanged. It requires the exact current answer reference and constrains model references to supplied governed references. It binds:

- `RESOLVED` to no material gap, follow-up, or contradiction reference;
- `NEEDS_FOLLOWUP` to a material gap and one follow-up;
- `CONTRADICTED` to a material gap and contradiction reference;
- `INSUFFICIENT_EVIDENCE` to a material gap with no follow-up;
- `UNANSWERED` to no follow-up.

Final repair evidence:

- targeted provider/validator/interview tests: 42/42 PASS;
- complete application regression: 133/133 PASS;
- exact-SHA application CI: PASS for `d8452cdf040d75360e711c994c2b911189d4842c`;
- Railway deployment: `533ddf19-a148-49dd-8574-30a75e5e15e1` — SUCCESS;
- Railway source commit: `d8452cdf040d75360e711c994c2b911189d4842c`;
- local app SHA == remote app SHA == Railway deployment SHA == served runtime git SHA;
- local and hosted canonical source-tree SHA-256: `a02e4bddbb7b3b68b661c7ce566c104f97ecc4e054bca5e5ebc5a7c6e30d36de`;
- graph status: PASS;
- Fast Filter: AVAILABLE;
- Human CRIT question status: READY;
- provider: `openai_api`;
- requested/resolved model: `gpt-6-luna`;
- `tools=false`;
- `store=false`;
- 3/3 fresh isolated live question-to-answer transactions completed without validator fallback;
- validator error code: null in all 3;
- valid live answer outcomes included both `RESOLVED` and `NEEDS_FOLLOWUP`;
- real Microsoft Edge render: PASS;
- live current question visible;
- resolved feedback visible;
- governed graph revision visible;
- `Request failed`: absent;
- `REVIEW_UNAVAILABLE`: absent;
- persistent Railway volume remains mounted at `/data`;
- production and both `main` branches remain untouched.

Foundation 06 hosted-staging acceptance is therefore PASS on the superseding exact candidate `d8452cdf040d75360e711c994c2b911189d4842c`. This accepts only the bounded staging architecture and live hosted CRIT provider path described in this contract. It does not authorize production promotion, any `main` merge, retrieval, graph-aware CRIT, convergence, planner removal, cross-project learning, or additional provider/model changes.

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

`PASS — FOUNDATION_06_HOSTED_STAGING_ACCEPTED`

Railway hosting, exact release identity, provider/model authority, live OpenAI CRIT semantic review, hardened answer-review contract, Fast Filter advisory boundary, persistence, browser rendering, and final deployment currentness are accepted on exact candidate `d8452cdf040d75360e711c994c2b911189d4842c` / deployment `533ddf19-a148-49dd-8574-30a75e5e15e1`. Foundation 06 is closed at this tranche boundary. No next tranche, production promotion, or `main` merge is authorized by this PASS.
