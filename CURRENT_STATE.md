# GACM Trial — Current State

## Authoritative repository

`chriskulbaba2025/gacm-trial`

## Current authoritative commit

`f059819e0384f3fa1591e1e3ba7784534372d9d4`

## Authoritative implementation PRD

`GACM_IMPLEMENTATION_PRD_V1.0.md`

## Methodology status

GACM v4.2.2 is treated as FROZEN methodology authority. This repository is for Pilot v1 implementation and evidence, not methodology redesign.

## Current phase

**Phase 1 — Control-Layer Audit**

No application implementation is authorized yet.

## Current objective

Audit every control expressed or implied by the Pilot v1 PRD and classify it by the lowest deterministic enforcement layer capable of preventing the failure.

Allowed layers:

- BUSINESS
- GOVERNANCE
- DURABLE AUTHORITY
- DISCOVERY / GRAPH
- ORCHESTRATION
- EXECUTION / GCU
- MODEL
- INDEPENDENT VERIFICATION
- RELEASE / SETTLE
- HUMAN JUDGMENT

## Required Phase 1 output

Create `GACM_CONTROL_LAYER_AUDIT_V1.md` containing, for every control:

1. Control ID
2. Control statement
3. Failure prevented
4. Current/assumed enforcement layer
5. Correct enforcement layer
6. Whether the model can bypass it
7. Whether stale memory can bypass it
8. Whether ambiguity can bypass it
9. Required machine enforcement
10. Required evidence/proof
11. Dependencies on other controls
12. Implementation priority

The audit must explicitly cover:

- GitHub authority
- Graphify discovery only, never authority
- authoritative operational context resolution
- account / tenant / environment / region / repository identity
- placeholder prevention
- model routing
- GCU execution boundaries
- independent verification
- bounded repair
- affected-scope re-verification
- broader requalification triggers
- durable run state
- rollback
- SETTLE
- human authority
- continuation across chats/sessions without chat memory

## Stop condition

Do not implement code, Graphify integration, model routing, or orchestration during Phase 1.

If the audit finds a contradiction in the PRD that prevents a deterministic control placement, document the contradiction and STOP rather than silently choosing a design.

## Next gate

Human review of `GACM_CONTROL_LAYER_AUDIT_V1.md`.

Only after HUMAN PASS may Phase 2 — Durable Run-State Schema begin.
