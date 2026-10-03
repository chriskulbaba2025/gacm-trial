# GACM MVP Closure Contract v1

**Status:** FROZEN CANDIDATE CONTRACT
**Effective:** 2026-10-03
**Applies to:** GACM MVP closure only
**Does not authorize:** merge, deployment, production mutation, model escalation, or V2 graph implementation

## 1. Purpose

This contract defines the finish line for the current GACM MVP and the only accepted closure sequence.

The objective is not to clear the next visible error. The objective is to prove the defined MVP as one governed system without expanding scope.

## 2. MVP boundary

The MVP includes the connected path:

`authority preflight → idea intake → Human CRIT → governed filtering/context → decision/PRD gate → bounded work package → governed execution → independent verification → bounded repair → release-currentness verification → real runtime/browser acceptance → promotion decision → SETTLE`

The MVP must preserve durable state across restart/reopen and must not depend on chat memory.

## 3. Explicit exclusions

The following are not required to close this MVP unless a proven blocker makes one unavoidable:

- Neo4j or another graph database;
- broad V2 governed change-intelligence graph implementation;
- vector retrieval;
- graph-aware convergence engines;
- autonomous learning or rule promotion;
- Hermes as primary executor;
- Laya integration;
- broad product redesign;
- production mutation.

V2 architecture remains a separate post-MVP implementation program.

## 4. Authority entry gate

Before any work unit starts, record and verify:

- repository;
- branch;
- exact starting SHA;
- upstream authority identities;
- worktree cleanliness;
- authorized environment;
- provider/service identity where external execution is required;
- model identity;
- credential provenance classification;
- production mutation authority;
- rollback target;
- frozen work-package definition of done.

Any mismatch is HOLD before implementation.

## 5. Work-package contract

Each work package must contain:

1. one measurable objective;
2. owning boundary and root-cause statement;
3. exact starting SHA;
4. permitted files;
5. prohibited files;
6. dependencies and downstream surfaces;
7. model authority;
8. external-provider classification;
9. exact test contract;
10. generalization contract;
11. rollback target;
12. stop conditions;
13. evidence outputs;
14. explicit promotion boundary.

Adjacent work may not be silently absorbed.

## 6. Execution policy

Default external Codex model:

`gpt-5.6-luna`

Mandatory rules:

- Luna is used first and remains the model unless a human explicitly authorizes another model.
- No Luna → Terra → Sol or other escalation chain may occur automatically.
- No subagent, child run, forked run, parallel agent, or extra model session may be created without explicit human authorization.
- One authorized work package is one execution boundary.
- No objective mutation during execution.
- No unbounded tool or model retry loops.
- A tool/runtime failure may receive one bounded alternate invocation when it does not change scope or authority; repeated infrastructure failure is HOLD.
- Maximum three failed repair attempts in one defect family, then stop and reset diagnosis.
- Production is read-only unless separately authorized.
- Paid or authenticated external calls require both provider authority and applicable spend authority.
- The executor may not issue authoritative final PASS.

## 7. Diagnosis rule

Before repair, identify:

- root cause;
- owning boundary;
- related failure modes;
- connected-system impact;
- blast radius;
- whether prior accepted proof is invalidated.

Do not repair named fixtures or isolated symptoms when a generic owning boundary explains them.

## 8. Repair rule

Repair the smallest generic owning boundary that satisfies the frozen definition of done.

During repair:

- run targeted tests first;
- do not repeatedly run the full suite after every edit;
- preserve unrelated files and accepted behaviour;
- do not add optional refactors;
- do not expand the work package to absorb newly discovered adjacent work.

If a newly discovered issue is required for the frozen MVP definition of done, register it under the current closure program. Otherwise defer it.

## 9. Generalization gate

MVP closure requires fresh materially different scenarios in addition to reference regression.

For variable-input Human CRIT behaviour, use at least three scenario classes:

1. strong / well-defined input;
2. mixed / partially defined input with meaningful gaps;
3. weak / ambiguous input requiring substantial clarification.

Across those scenarios prove:

- the same generic path is used;
- questions and gaps change with the input;
- known strengths are preserved;
- unknowns remain unknown;
- weak input does not manufacture certainty;
- filtering remains advisory only;
- no named fixture controls generic logic;
- persistence/reopen preserves exact lineage;
- PRD readiness follows governed evidence and human authority.

Reference examples are regression-only evidence.

## 10. Whole-system acceptance

The final candidate must prove, on exact identity:

- authoritative repository/currentness resolution;
- exact upstream SPEC and CRIT authority;
- provider/model authority;
- idea/input preservation;
- Human CRIT adaptive path;
- filtering authority boundary;
- UNKNOWN/PARTIAL/UNAVAILABLE/CONFLICTED semantics where applicable;
- PRD gate;
- human approve/revise/defer/stop boundaries;
- persistence and reopen continuity;
- cross-record isolation;
- interrupted execution/recovery where applicable;
- bounded execution scope;
- repair-limit enforcement;
- independent verification;
- rollback availability;
- full regression;
- release-currentness identity;
- real runtime/browser acceptance;
- SETTLE.

Missing proof is HOLD, not PASS.

## 11. Release-currentness invariant

Before TEAM UAT, MVP acceptance, staging freeze, or production promotion, prove:

`accepted candidate SHA = remote candidate SHA = deployed artifact SHA = served runtime identity`

Where a stage is not applicable, record `NOT_APPLICABLE`; do not omit it.

A stale reviewer/browser/runtime invalidates release acceptance even if prior tests passed.

## 12. Browser/runtime rule

When the MVP includes a browser surface, acceptance requires the real application path, not only mocked HTTP or unit proof.

Verify at minimum:

- fresh load;
- idea creation/input;
- Human CRIT interaction;
- save/reopen or reload;
- continuity of answers and provenance;
- PRD readiness behaviour;
- visible unknown/gap behaviour;
- no internal governance/process leakage that confuses the human user;
- exact runtime identity.

## 13. Independent verification

The implementation executor cannot certify its own final PASS.

Independent verification must inspect the exact candidate and raw evidence, including:

- changed-file scope;
- exact-head tests;
- generalization;
- currentness;
- browser/runtime proof;
- forbidden changes;
- rollback identity;
- production mutation state.

Authoritative outcomes are:

`PASS | FAIL | HOLD | UNOBSERVABLE`

Do not collapse these states.

## 14. Closure sequence

The MVP closure program follows this order:

`AUDIT → DEFECT REGISTER → ROOT CAUSES → REPAIR OWNING BOUNDARIES → TARGETED TESTS → FULL REGRESSION → RE-AUDIT → REPAIR IF REQUIRED → RETEST → CURRENTNESS → REAL RUNTIME/BROWSER → FINAL ADVERSARIAL AUDIT → PROMOTION DECISION → SETTLE → CLOSE`

Do not skip directly from local regression to promotion.

## 15. Final acceptance command

Before MVP PASS, the repositories must expose a deterministic acceptance entrypoint or equivalent orchestration that runs the required machine-verifiable gates and exits non-zero on failure.

It must report each gate separately and identify the exact candidate SHA.

This tranche freezes the requirement; it does not implement that command.

## 16. Evidence rule

Consequential execution must create a dedicated proof set.

Each proof set records:

- starting SHA;
- final SHA;
- exact changed files;
- tests and exit codes;
- generalization scenarios;
- independent verification result;
- currentness identities;
- runtime/browser evidence;
- promotion state;
- SETTLE state;
- unresolved HOLD items.

No prose-only PASS is authoritative.

## 17. MVP definition of done

GACM MVP is complete only when all of the following are true on one exact accepted candidate:

- [ ] authority manifest resolves without contradiction;
- [ ] Human CRIT candidate is durably reconstructable;
- [ ] frozen work-package execution rules are machine-enforced where deterministic enforcement is possible;
- [ ] Luna-first/no-autonomous-escalation policy is enforced for external Codex execution;
- [ ] no autonomous subagent or extra-session expansion is possible without explicit authority;
- [ ] whole-system audit has no unresolved MVP-critical defect;
- [ ] strong/mixed/weak generalization passes;
- [ ] full regression passes;
- [ ] exact candidate receives independent verification;
- [ ] release-currentness identity passes;
- [ ] real runtime/browser acceptance passes;
- [ ] rollback target is proven;
- [ ] promotion is explicitly authorized;
- [ ] post-promotion SETTLE passes;
- [ ] durable closure record is written.

Until every applicable item is proven:

`MVP STATUS = HOLD`

## 18. Tranche boundary

GACM-MVP-CLOSURE-00 ends after:

- recovered candidate authority is durably preserved;
- governance/app/SPEC/CRIT identities are frozen;
- this closure contract is committed as a candidate;
- `CURRENT_STATE.md` is reconciled on the closure candidate;
- regression confirms no governance implementation break.

It does not authorize merge or promotion.

The next tranche begins only after explicit authorization.
