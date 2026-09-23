# GACM Version 2 — Product Architecture and Roadmap

Status: **Future-state roadmap / intent capture**
Repository: `chriskulbaba2025/gacm-trial`
Purpose: Preserve the agreed Version 2 product direction without changing the current accepted GACM authority or implementation baseline.

## 1. Version 2 product direction

GACM should evolve from a governed change-management engine into a broader operating system for SMBs that want to build, run, improve, and govern AI-enabled products, automations, agents, and workflows without needing a large internal technical team.

The intended product promise is:

> Turn a business idea into a challenged, governed, tested product or workflow, then keep managing and improving it over time.

Version 2 should support the full lifecycle:

**Idea → CRIT interview → answer-quality drilling → scoring → PRD → human approval → governed implementation tranches → worker-agent execution → testing and proofs → whole-system repair → release decision → ongoing monitoring and management.**

## 2. Core architectural roles

### CRIT — human reasoning and interview layer

CRIT should be used as the authoritative human-facing reasoning process.

Its role is to:
- understand the business idea and context;
- ask one high-value question at a time;
- inspect prior answers before asking more;
- challenge vague, incomplete, contradictory, or weak answers;
- drill down until the answer is sufficiently complete for the decision being made;
- stop asking when more questioning is unlikely to materially improve the result;
- preserve human authority over value, risk, and final decisions.

GACM should adopt the existing CRIT skill rather than recreate a parallel interview framework.

### GACM — governor and orchestrator

GACM remains the authority for:
- scope freeze;
- requirement identity;
- evidence and provenance;
- human approval gates;
- change authorization;
- tranche creation;
- execution permissions;
- testing requirements;
- regression gates;
- proof collection;
- defect tracking;
- repair-cycle limits;
- release/promotion decisions;
- immutable change history;
- reusable learning.

GACM should govern work without becoming dependent on any one coding or agent platform.

### Worker agents — interchangeable executors

Codex, Hermes, Paperclip, and future tools should be treated as interchangeable workers beneath GACM.

GACM should choose or authorize workers based on the work required rather than binding the architecture to one provider.

Workers may perform:
- coding;
- testing;
- research;
- file changes;
- browser tasks;
- infrastructure work;
- documentation;
- analysis;
- repair tasks.

No worker should be able to weaken its own governance controls, acceptance tests, authority records, or release gates.

## 3. Answer-quality loop before PRD generation

Version 2 must go beyond checking whether a field has been filled in.

For every important CRIT answer, the system should assess:
- completeness;
- specificity;
- ambiguity;
- internal consistency;
- decision usefulness;
- material unknowns;
- unsupported assumptions;
- whether the answer is strong enough to support downstream decisions.

If an answer is not sufficient, CRIT should ask the smallest number of targeted follow-up questions needed to improve it before moving on.

The system must distinguish:
- USER_STATED;
- ASSUMED;
- INFERRED;
- EVIDENCED;
- UNKNOWN.

A completed answer must not automatically become a proven fact.

## 4. Governed PRD creation

Once CRIT and GACM determine that sufficient information exists, GACM should generate a plain-language PRD.

The PRD should include at minimum:
- product or workflow name;
- executive summary;
- problem;
- target user;
- desired outcome;
- current workflow/problem state;
- proposed solution;
- user workflow;
- core capabilities;
- evidence and evidence gaps;
- assumptions;
- constraints;
- risks;
- dependencies;
- guardrails;
- success measures;
- out-of-scope items;
- open questions;
- acceptance criteria;
- MVP definition;
- recommended next governed step.

The PRD remains draft until explicit human approval.

Known gaps and accepted assumptions must remain visible.

## 5. PRD-to-Codex / worker tranche planner

After human PRD approval, GACM should automatically create a governed implementation plan.

Each tranche should contain:
- tranche purpose;
- exact scope;
- authoritative requirements;
- dependencies;
- likely files/systems affected;
- permitted actions;
- prohibited actions;
- acceptance criteria;
- targeted tests;
- whole-system regression requirements;
- negative/adversarial tests;
- proof/report outputs;
- repair-cycle cap;
- stop/hold conditions;
- exact worker prompt;
- required human approval, if any.

Tranches should be ordered by dependency and risk.

A worker may continue through multiple authorized tranches without unnecessary human interruption when all gates pass.

## 6. Tip-to-tail troubleshooting and autonomous repair

Version 2 must incorporate the improved repair process proven during recent PRYSM and COMPAS2 work.

GACM must not stop at the first visible defect.

Required repair cycle:

**Freeze authority → map the full system path → inspect connected failure surfaces → identify root-cause groups → repair at the correct shared layer → run targeted tests → run dependency tests → run whole-system regression → run negative/adversarial checks → verify persistence/reload/report continuity → record proof → continue automatically.**

Key rules:
- inspect the whole system rather than applying isolated patches;
- identify interacting and converging defects;
- distinguish symptoms from root causes;
- repair the highest correct abstraction layer;
- determine what else the repair could affect before changing code;
- re-test the entire relevant system after repair;
- continue automatically to the next defect when authorized;
- maximum three repair attempts for the same root cause;
- after three unresolved attempts, declare RESET_REQUIRED or HOLD rather than patch indefinitely;
- preserve production unless explicitly authorized.

The goal is to eliminate the recurring “fix one thing, find five more later” pattern.

## 7. Ongoing management layer

GACM Version 2 should remain useful after the initial product or workflow is built.

This creates the recurring-value / MRR model.

Ongoing functions should include:
- monitor product/workflow health;
- detect defects and regressions;
- detect broken integrations;
- detect model/provider changes that affect behavior;
- monitor unresolved risks;
- manage future feature requests through CRIT and GACM;
- re-audit products periodically;
- manage repair and improvement tranches;
- retain change history;
- report what changed and why;
- track human approvals;
- surface work requiring attention;
- manage multiple AI products/workflows for one business.

This turns GACM into an SMB AI-management platform, not only a build tool.

## 8. Storage architecture

Graph memory should remain the relationship and reasoning memory layer, not become the only storage system.

### Graph memory
Use for:
- requirements;
- decisions;
- dependencies;
- relationships;
- evidence links;
- defects;
- causal chains;
- risks;
- provenance;
- learning;
- cross-artifact relationships.

### Relational operational store
Use for:
- users;
- organizations;
- projects;
- workflow state;
- tranche state;
- permissions;
- approvals;
- task state;
- execution state;
- costs;
- timestamps;
- current operational records.

### Object/artifact storage
Use for:
- source documents;
- screenshots;
- logs;
- builds;
- test evidence;
- reports;
- PRDs;
- exported artifacts;
- large proof files;
- historical generated outputs.

Do not force large binary or report artifacts into the graph.

## 9. Management and reporting experience

The SMB-facing interface should be simple and non-technical.

The main dashboard should answer:
- What is running?
- What changed?
- What is healthy?
- What is broken?
- What did AI repair?
- What still needs human approval?
- What risks are open?
- What is costing money?
- What should we do next?
- Are products/workflows getting better or worse?

Recommended reporting areas:
- portfolio health;
- product/workflow health;
- active changes;
- blocked work;
- recent repairs;
- unresolved risks;
- model/provider dependencies;
- cost and usage;
- human approvals;
- release history;
- improvement opportunities;
- recurring audit status.

Technical evidence, hashes, raw logs, and provenance should remain available behind deeper governance/audit views.

## 10. Commercial positioning

Primary Version 2 positioning:

> GACM helps SMBs turn ideas into governed, tested AI-enabled products and workflows, then run and improve them over time without needing a large internal technical team.

The value is broader than replacing a junior developer.

It can compress work normally distributed across:
- junior development;
- QA;
- technical project coordination;
- product analysis;
- troubleshooting;
- documentation;
- change control;
- operational monitoring.

The stronger recurring value is:

**Build with GACM once. Manage and improve with GACM every month.**

Potential recurring pricing should be based more on active products/workflows and level of monitoring/governance than simple seat count.

## 11. Version 2 architectural flow

**CRIT → GACM → governed PRD → tranche planner → worker agents (Codex / Hermes / Paperclip / others) → tests and proofs → whole-system repair loop → governed release → graph + relational + artifact storage → ongoing monitoring → SMB management dashboard.**

## 12. Guardrails

Version 2 must preserve these principles:
- automate analysis and execution, not final human judgment;
- no silent conversion of assumptions into facts;
- no unsupported PASS;
- no worker can change its own gates;
- evidence and provenance remain traceable;
- approved artifacts remain immutable/versioned;
- production changes require explicit authority;
- paid/external operations remain governed;
- whole-system impact must be considered before repair;
- failures should improve reusable GACM learning when the pattern is universal;
- implementation workers remain replaceable.

## 13. Not yet authorized for current implementation

This file is a Version 2 roadmap and memory artifact.

It does **not** authorize immediate implementation, production changes, provider integration, paid calls, new infrastructure, or modification of the current accepted GACM baseline.

Future implementation should begin from the latest explicitly approved GACM authority and be decomposed into governed tranches before code changes are made.

## 14. Governed Change Intelligence Graph — detailed architecture

The governed reasoning-graph direction is now specified in:

GACM_V2_GOVERNED_CHANGE_INTELLIGENCE_GRAPH.md

That document is the detailed Version 2 architecture authority for graph reasoning, provenance, epistemic state, graph mutation, hybrid retrieval, convergence detection, historical failure-pattern learning, tenant isolation, rollback/reconstruction, release-currentness integration, independent verification, adversarial acceptance, and implementation order.

The reasoning graph remains a governed projection rather than a replacement for GitHub/durable authority, relational operational state, Graphify discovery, artifact storage, or independent verification.

This roadmap does not authorize implementation of that architecture. Implementation requires a separately governed PRD/tranche.

## 15. Final architecture hardening status

The final pre-implementation architecture audit is recorded in:

GACM_V2_FINAL_ARCHITECTURE_HARDENING_AUDIT.md

The detailed graph architecture now includes canonical entity identity, explicit conflict sets, evidence-independence controls, epistemic path composition, operational-state/graph consistency, retrieval negative semantics, mutation impact classes, reasoning provenance, measurable graph-value tests, convergence negative controls, performance/cost budgets, deletion/retention reconciliation, backup/restore proof, migration controls, and prerequisite control-plane enforcement.

Architecture discovery should stop here unless implementation reveals a concrete contradiction or missing control.

The next governed artifact should be the Version 2 implementation PRD/tranche plan.

