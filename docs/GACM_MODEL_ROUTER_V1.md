# GACM Pilot v1 Model Router

**Phase:** 6 - Model Router
**Status:** deterministic pilot implementation

## Purpose

The router selects the minimum sufficiently capable qualified model for one
bounded work unit. It is an orchestration decision. The execution model cannot
choose, override, or certify its own route.

## Routing dimensions

Every work unit supplies an integer score from 0 (none) through 4 (highest)
for task complexity, ambiguity, blast radius, architectural impact, authority
sensitivity, security sensitivity, reasoning depth, repair complexity, and
verification complexity. The router chooses the highest required capability
using a fixed dimension order for deterministic ties. Scores are explicit
inputs owned by GACM; no LLM scores its own suitability.

Architectural, security, and authority scores of 3 or 4 require the
architecture class. Other scores of 3 or 4 also require architecture. A score
of 2 requires precision. Scores 0 or 1 require mechanical capability.

## Capability classes and registry

The registry is a configurable tuple of qualification receipts. Each receipt
contains the provider, configurable model identifier, capability class,
qualification identity, maximum qualified dimension score, cost rank, and
current qualification status. The pilot default registry contains configurable
identifiers for Luna (mechanical), Terra (precision), and Sol (architecture).
Names are not embedded in routing rules.

A candidate is eligible only when it is currently qualified, its class meets
the required class, and its qualified score envelope covers the highest work
unit score. If no candidate is eligible, routing raises `BLOCKED`; there is no
silent fallback.

## Selection and cost

The router first filters by qualification and capability. It selects the
lowest capability class that satisfies the work unit. Cost rank is consulted
only among candidates in that same minimum class. A cheaper under-qualified
model can never win.

## Escalation

`escalate()` evaluates the work unit again and creates a new routing decision.
The new receipt has a distinct decision ID, `escalation_required: true`, and
`supersedes_decision_id` pointing to the prior decision. The prior decision is
not mutated and remains available as durable evidence; callers project the
ordered prior/current receipts through `routing_history` in Phase 2 state.
Luna to Terra and Terra to Sol are supported when the new risk envelope
requires them. If no higher qualified candidate exists, the result is
`BLOCKED`.

## Durable run-state integration

`RoutingDecision.to_run_state_model()` projects the selected model, provider,
qualification identity, route reason, timestamp, and the complete routing
decision into the Phase 2 `work_units[].model` receipt. The Phase 2 schema now
accepts the optional `routing_decision` object while retaining its existing
verification contract. A routing receipt contains no verification status and
cannot create authoritative PASS. Only the independent verifier can issue
authoritative PASS.

## Determinism and authority boundary

Given identical work-unit dimensions, registry entries, and clock input, the
selection and decision identity are identical. The runtime timestamp records
when a decision was made; deterministic tests inject a clock. An optional
execution-model argument is intentionally ignored for selection. This keeps
model preference, prompt instructions, cost preference, and model self-report
outside the routing authority.

The registry and risk policy are code/configuration authority. The model may
execute within the routed envelope, but cannot alter the route, qualification,
durable identity, or verification authority.
