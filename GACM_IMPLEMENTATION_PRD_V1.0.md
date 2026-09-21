# GACM Implementation PRD — Pilot v1.0

**Product:** Governed Autonomous Change Management (GACM)  
**Methodology authority:** GACM v4.2.2 FROZEN  
**Status:** Implementation PRD  
**Pilot strategy:** Real project, isolated fork/branch/worktree, stable project preserved as rollback authority  
**Primary execution framework:** GCU  
**Authority store:** GitHub / version-controlled durable state  
**Discovery layer:** Graphify  
**Autonomous execution engine:** Existing harness/Codex for Pilot v1  
**Hermes:** Deferred until GACM control boundaries are proven

## 1. Product purpose

GACM is a control plane for longer, increasingly autonomous software-change runs. It must govern authoritative state, operational identity, task scope, model selection, execution permissions, verification, bounded repair, re-verification, promotion, settlement, and rollback.

Target flow:

```text
PRD
 ↓
Authoritative State Resolution
 ↓
Graphify Context Discovery
 ↓
GACM Planning + Risk Classification
 ↓
Model Routing
 ↓
GCU Bounded Execution
 ↓
Independent Verification
 ↓
PASS → Continue
FAIL → Scoped Diagnosis → Local Repair → Affected-Scope Reverification
 ↓
Final Release Verification
 ↓
Promotion Intent
 ↓
Deployment / Publication
 ↓
SETTLE
 ↓
Durable Completion
```

## 2. Root problem

Current agentic coding systems can execute significant work, but reliability falls during longer runs because controls are often enforced at the wrong layer. Examples include SOPs telling a model to retrieve an account ID instead of the system retrieving it deterministically, chat memory being treated as authority, local repairs causing unnecessary full reruns, execution agents certifying their own work, model choice being based on convenience rather than risk, placeholders being used when authoritative values already exist, related project state not being discovered, repairs changing unrelated surfaces, deployment success being treated as completion, and inability to reconstruct exactly what state produced an outcome.

GACM moves these controls out of probabilistic instructions and into enforceable system layers.

## 3. Product principle

**A control belongs at the lowest layer capable of enforcing it deterministically.**

Prompts may explain desired behaviour. Prompts must not be the only enforcement mechanism for safety-critical or authority-critical controls.

## 4. Authority model

GitHub and approved version-controlled durable state remain authoritative.

Authority order:

```text
Approved durable state
↓
Current governed project state
↓
Retrieved operational context
↓
Execution context
↓
Model/harness memory
↓
Chat context
```

Chat, model memory, and harness memory are not authoritative. GACM must fail closed when required authority cannot be uniquely established.

## 5. Graphify role

Graphify is the discovery and relationship layer, not the authority layer. It should index approved project sources such as repositories, source code, configuration, documentation, SQL schemas, architecture files, SOPs, account mappings, environment definitions, and deployment information.

Any material fact obtained through Graphify must resolve back to an authoritative source before execution relies on it.

Architecture:

```text
GitHub = authority
Graphify = discovery
GACM = governance
GCU = governed implementation
LLM = bounded reasoning/execution
```

## 6. Authoritative Operational Context Resolver

GACM must resolve operational identity before account-sensitive or environment-sensitive work begins. This applies to client, project, repository, branch, environment, cloud account, tenant, region, deployment target, service, database, credential reference, domain, external integration, and production/staging identity.

The resolver must produce exactly one authoritative execution context. If multiple candidates remain, execution must STOP with `AUTHORITY_AMBIGUOUS`. The model must not guess.

## 7. Placeholder prevention

A known authoritative value must never be replaced with a placeholder. The output validator must detect operational placeholders such as `<ACCOUNT_ID>`, `YOUR_ACCOUNT`, `YOUR_REGION`, `YOUR_REPO`, `replace_this`, `insert_your`, or example account values when authoritative data already exists.

If an authoritative value does not exist, execution stops rather than inventing one.

## 8. Model routing

GACM selects the minimum sufficiently capable qualified model for the highest meaningful risk dimension. Cost may influence selection only after capability requirements are satisfied.

Routing dimensions include task complexity, ambiguity, blast radius, architectural impact, security sensitivity, authority sensitivity, reasoning depth, repair complexity, and verification complexity.

Pilot routing:

```text
Luna → mechanical / bounded implementation
Terra → precision / nuanced repair / language
Sol → architecture / difficult diagnosis / high-risk reasoning
```

The model does not own its own qualification decision.

## 9. GCU role

GCU is the governed implementation engine inside GACM. GCU remains responsible for authority discovery, diagnosis, implementation, local testing, bounded repair, evidence generation, and traceability.

GCU cannot produce authoritative final PASS. GACM wraps GCU with authority, routing, permissions, independent verification, durable state, promotion, settlement, and rollback.

## 10. Long-run structure

Long autonomous runs must be decomposed into bounded work units. Each unit has input state, expected outcome, allowed surfaces, model, risk class, test contract, stop conditions, and output evidence.

A failure does not automatically invalidate all prior successful units.

## 11. Bounded repair

When verification fails, GACM must determine the smallest affected scope. After repairing a failed unit, re-run that unit's verification plus dependent tests affected by the repair. Do not automatically rerun previously passed independent units.

A complete model-bearing pass is required only when the repair affects a surface that invalidates previous assurance, including architecture contracts, shared authority, model-bearing prompts, global configuration, shared schemas, security boundaries, verification infrastructure, or high-blast-radius dependencies.

This distinction must be machine-enforced rather than decided casually by the execution agent.

## 12. Independent verification

The execution agent cannot be the final authority on whether its work passed. Independent verification evaluates expected outcome, scope preservation, regression impact, authority integrity, operational identity, forbidden changes, required tests, artifact identity, and deployment identity where relevant.

Verification states:

```text
PASS
FAIL
BLOCKED
UNOBSERVABLE
```

Only the independent verification layer may produce authoritative PASS.

## 13. Durable run state

Each run requires durable state including run ID, project ID, authoritative starting SHA, branch/worktree, PRD identity, GACM version, Graphify index identity, operational context, task units, model used per unit, model qualification identity, inputs, outputs, tests, failures, repairs, affected scope, verification decisions, human interventions, promotion state, deployment identity, settlement state, and rollback target.

A new chat must be able to reconstruct the run without relying on conversational memory.

## 14. Rollback

The first pilot must run against a forked or isolated project state. The current stable project remains untouched and authoritative. If the GACM run becomes unreliable, STOP, preserve evidence, abandon experimental state, and return to known-good authority.

## 15. SETTLE

Release is not completion. After promotion or deployment, GACM must observe the released system. SETTLE verifies that actual released behaviour matches the promoted candidate. For high-risk changes, observation cannot rely solely on instrumentation located inside the changed blast radius.

States:

```text
SETTLING
SETTLED
FAILED
UNOBSERVABLE
```

Only after SETTLED may durable completion be recorded where settlement is required.

## 16. Pilot v1 exclusions

Pilot v1 does not include model weight modification, continual neural training, autonomous methodology rewriting, autonomous GACM rule modification, Hermes as the primary execution engine, self-promotion of learned policies, unrestricted cross-project learning, or automatic universalization of project-specific knowledge.

## 17. Hermes boundary

Hermes is a later execution adapter. Before Hermes integration, GACM must prove ownership of authority, retrieval, model routing, permissions, verification, repair scope, promotion, and rollback. Hermes may later adapt execution; GACM remains the authority deciding whether that adaptation is accepted.

## 18. First pilot

The first pilot uses an existing active project where moderate changes are already planned. Requirements: known-good project state, isolated fork/branch/worktree, multiple dependent steps, meaningful model routing and verification, recoverable failure, no unnecessary production risk, and a normal human-driven process available as comparison baseline.

The pilot should exercise authority discovery, Graphify discovery, context resolution, planning, model routing, GCU execution, independent verification, bounded repair, scoped re-verification, durable state, and final release decision.

## 19. Pilot measurements

Measure percent of work completed without human intervention, human interventions, authority-resolution failures, incorrect account/environment selections, placeholder violations, model-routing escalations, verification failures, local repairs, full reruns avoided, regressions detected, scope violations, rollback events, tokens, model cost, wall-clock duration, model execution duration, and human supervision time.

## 20. Acceptance criteria

Pilot v1 passes only if:

1. GitHub durable state remains authoritative.
2. Graphify is discovery/index infrastructure only.
3. Required operational identities resolve before sensitive execution.
4. Ambiguous authority produces STOP.
5. Known values cannot be replaced with placeholders.
6. Model routing is controlled by GACM.
7. GCU performs bounded implementation.
8. Execution cannot declare authoritative PASS.
9. Verification can identify affected repair scope.
10. Local repairs do not automatically trigger full reruns.
11. Model-bearing or authority-bearing changes trigger broader requalification where required.
12. Run state survives loss of the originating chat.
13. Every promoted state has reproducible identity.
14. Stable rollback remains available.
15. Release requires SETTLE where applicable.
16. The pilot produces a complete evidence trail.

## 21. Fixed implementation sequence

```text
1. Control-Layer Audit
2. Durable Run-State Schema
3. GitHub Authority Resolver
4. Graphify Discovery Adapter
5. Authoritative Operational Context Resolver
6. Model Router
7. GCU Execution Adapter
8. Independent Verification Engine
9. Repair-Scope / Dependency Logic
10. Placeholder + Identity Validator
11. Promotion / Rollback State Machine
12. SETTLE Logic
13. Pilot Harness
14. Real Project Pilot
15. Evidence Review
```

Do not begin Hermes integration before this pilot passes.

## 22. Control-Layer Audit contract

Before implementation, every GACM control must be classified by enforcement layer.

Allowed layers:

```text
BUSINESS
GOVERNANCE
DURABLE AUTHORITY
DISCOVERY / GRAPH
ORCHESTRATION
EXECUTION / GCU
MODEL
INDEPENDENT VERIFICATION
RELEASE / SETTLE
HUMAN JUDGMENT
```

For every current rule, determine: what failure it prevents, where it is currently enforced, the lowest layer capable of enforcing it, whether the model can bypass it, whether stale memory can bypass it, whether ambiguity can bypass it, and what evidence proves enforcement.

Any safety-critical rule enforced only by a prompt must be reviewed for relocation.

## 23. Definition of done

GACM Pilot v1 is complete when an isolated real-project change can begin from an approved PRD and progress through multiple autonomous implementation and repair cycles while maintaining correct authority, retrieving correct operational context, selecting models appropriately, limiting change scope, independently verifying outcomes, repairing only affected scope, preserving complete durable evidence, maintaining a stable rollback point, and reaching a governed final release decision without requiring continuous human supervision.

## 24. Product boundary

GACM is not an autonomous developer.

GACM is the governance system that makes increasingly autonomous development trustworthy.

Its job is not to make the model smarter. Its job is to ensure that intelligence operates against the correct authority, within the correct boundaries, with independently verified evidence, and with a recoverable path when it is wrong.


## 25. Mandatory generalization and whole-system repair gate

Governed product repairs are subject to the fail-closed `GACM-GENERALIZATION-AND-WHOLE-SYSTEM-GATE`.

Before diagnosis or code changes, GACM must freeze the product-level definition of done and map the connected system inside the authorized capability. Named fixtures, records, IDs, documents, URLs, screenshots, scores, or customer examples are regression evidence only and may not silently become the implementation target.

The frozen acceptance boundary remains fixed throughout the work unit. Defects found inside that boundary remain part of the same authorized repair unless they cross an authorization boundary, require an unsafe or production-forbidden action, are a genuinely separate product capability, or depend on an external condition that cannot be resolved in the authorized environment.

Repair must occur at the generic owning boundary. Fixture-specific branches, hard-coded IDs, named-case logic, expected-output patches, test-only production fallbacks, or contract weakening solely to satisfy one example are prohibited.

Before closure, GACM requires at least two fresh materially different valid input scenarios when the product domain supports variable inputs. They must traverse the same generic runtime path and prove all required boundaries through durable output and downstream continuity. Reference regression is separate proof and cannot substitute for generalization.

The gate must fail closed when generalized scenarios are missing or skipped, only the original reference case was tested, the generic path cannot be proven, required save/reopen or downstream continuity is unproven, fixture dependencies are detected, the frozen acceptance boundary changed, required security/privacy/isolation checks are unproven, or full regression is missing.

The gate is machine-enforced in orchestration and promotion eligibility. Promotion re-evaluates raw independent generalization evidence against the frozen contract; executor prose or a claimed PASS cannot override it.

Permanent escape classes are `FIXTURE_TARGET_COLLAPSE` and `SEQUENTIAL_BLOCKER_TUNNELING`. Future adversarial audits must explicitly challenge both.

Universal acceptance model:

`variable valid input → generic system path → durable output → downstream continuity → generalized acceptance`

The COMPAS2 `GCU-GENERALIZATION-01` pilot is a reference implementation only. Universal GACM must remain domain-independent.
