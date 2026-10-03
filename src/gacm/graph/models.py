"""Typed contracts for the governed GACM reasoning graph."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)


def content_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


class EpistemicState(StrEnum):
    USER_STATED = "USER_STATED"
    OBSERVED = "OBSERVED"
    EVIDENCED = "EVIDENCED"
    INFERRED = "INFERRED"
    HYPOTHESIS = "HYPOTHESIS"
    CONFLICTED = "CONFLICTED"
    ACCEPTED = "ACCEPTED"
    SUPERSEDED = "SUPERSEDED"
    UNKNOWN = "UNKNOWN"


class NodeType(StrEnum):
    REQUIREMENT = "Requirement"
    BUSINESS_GOAL = "BusinessGoal"
    USER_NEED = "UserNeed"
    ASSUMPTION = "Assumption"
    UNKNOWN = "Unknown"
    EVIDENCE = "Evidence"
    EVIDENCE_GAP = "EvidenceGap"
    DECISION = "Decision"
    CONSTRAINT = "Constraint"
    RISK = "Risk"
    DEPENDENCY = "Dependency"
    DEFECT = "Defect"
    ROOT_CAUSE = "RootCause"
    FAILURE_PATTERN = "FailurePattern"
    CHANGE = "Change"
    TEST = "Test"
    GATE = "Gate"
    ARTIFACT = "Artifact"
    SYSTEM = "System"
    COMPONENT = "Component"
    CONTRACT = "Contract"
    STATE_TRANSITION = "StateTransition"
    TRANCHE = "Tranche"
    HUMAN_APPROVAL = "HumanApproval"
    RELEASE_IDENTITY = "ReleaseIdentity"


class EdgeType(StrEnum):
    DEPENDS_ON = "DEPENDS_ON"
    AFFECTS = "AFFECTS"
    VERIFIED_BY = "VERIFIED_BY"
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    OBSERVED_IN = "OBSERVED_IN"
    POSSIBLY_CAUSED_BY = "POSSIBLY_CAUSED_BY"
    MAY_SHARE_CAUSE_WITH = "MAY_SHARE_CAUSE_WITH"
    EXPLAINS = "EXPLAINS"
    ADDRESSES = "ADDRESSES"
    REQUIRES = "REQUIRES"
    DETECTED = "DETECTED"
    BLOCKED_BY = "BLOCKED_BY"
    SUPERSEDES = "SUPERSEDES"
    BASED_ON = "BASED_ON"
    IMPLEMENTS = "IMPLEMENTS"


class ProducerRole(StrEnum):
    USER = "USER"
    HUMAN = "HUMAN"
    GACM_GOVERNANCE = "GACM_GOVERNANCE"
    ORCHESTRATION = "ORCHESTRATION"
    EXECUTOR = "EXECUTOR"
    INDEPENDENT_VERIFIER = "INDEPENDENT_VERIFIER"
    RELEASE_AUTHORITY = "RELEASE_AUTHORITY"
    SYSTEM = "SYSTEM"
    DISCOVERY = "DISCOVERY"


@dataclass(frozen=True)
class GraphNode:
    object_id: str
    project_id: str
    object_type: NodeType | str
    epistemic_state: EpistemicState | str
    status: str
    source: str
    created_at: str
    organization_id: str | None = None
    run_id: str | None = None
    source_snapshot_id: str | None = None
    provenance: tuple[str, ...] = ()
    authority_ref: str | None = None
    authority_digest: str | None = None
    producer_role: ProducerRole | str = ProducerRole.ORCHESTRATION
    verification_state: str = "NOT_VERIFIED"
    confidence: float | None = None
    valid_from: str | None = None
    valid_to: str | None = None
    superseded_by: str | None = None
    schema_version: str = "1.0.0"
    payload: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "object_id": self.object_id,
            "project_id": self.project_id,
            "organization_id": self.organization_id,
            "run_id": self.run_id,
            "object_type": str(self.object_type),
            "epistemic_state": str(self.epistemic_state),
            "status": self.status,
            "source": self.source,
            "source_snapshot_id": self.source_snapshot_id,
            "provenance": list(self.provenance),
            "authority_ref": self.authority_ref,
            "authority_digest": self.authority_digest,
            "producer_role": str(self.producer_role),
            "verification_state": self.verification_state,
            "confidence": self.confidence,
            "created_at": self.created_at,
            "valid_from": self.valid_from,
            "valid_to": self.valid_to,
            "superseded_by": self.superseded_by,
            "schema_version": self.schema_version,
            "payload": dict(self.payload),
        }

    def digest(self) -> str:
        return content_digest(self.to_dict())


@dataclass(frozen=True)
class GraphEdge:
    edge_id: str
    project_id: str
    relationship: EdgeType | str
    from_id: str
    to_id: str
    epistemic_state: EpistemicState | str
    source: str
    created_at: str
    organization_id: str | None = None
    run_id: str | None = None
    source_snapshot_id: str | None = None
    provenance: tuple[str, ...] = ()
    authority_ref: str | None = None
    authority_digest: str | None = None
    producer_role: ProducerRole | str = ProducerRole.ORCHESTRATION
    verification_state: str = "NOT_VERIFIED"
    confidence: float | None = None
    valid_from: str | None = None
    valid_to: str | None = None
    superseded_by: str | None = None
    schema_version: str = "1.0.0"
    payload: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "project_id": self.project_id,
            "organization_id": self.organization_id,
            "run_id": self.run_id,
            "relationship": str(self.relationship),
            "from_id": self.from_id,
            "to_id": self.to_id,
            "epistemic_state": str(self.epistemic_state),
            "source": self.source,
            "source_snapshot_id": self.source_snapshot_id,
            "provenance": list(self.provenance),
            "authority_ref": self.authority_ref,
            "authority_digest": self.authority_digest,
            "producer_role": str(self.producer_role),
            "verification_state": self.verification_state,
            "confidence": self.confidence,
            "created_at": self.created_at,
            "valid_from": self.valid_from,
            "valid_to": self.valid_to,
            "superseded_by": self.superseded_by,
            "schema_version": self.schema_version,
            "payload": dict(self.payload),
        }

    def digest(self) -> str:
        return content_digest(self.to_dict())


@dataclass(frozen=True)
class GraphMutation:
    mutation_id: str
    project_id: str
    expected_revision: int
    actor_role: ProducerRole | str
    idempotency_key: str
    nodes: tuple[GraphNode, ...] = ()
    edges: tuple[GraphEdge, ...] = ()
    rationale: str = ""
    evidence_refs: tuple[str, ...] = ()
    authority_refs: tuple[str, ...] = ()
    timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "mutation_id": self.mutation_id,
            "project_id": self.project_id,
            "expected_revision": self.expected_revision,
            "actor_role": str(self.actor_role),
            "idempotency_key": self.idempotency_key,
            "nodes": [item.to_dict() for item in self.nodes],
            "edges": [item.to_dict() for item in self.edges],
            "rationale": self.rationale,
            "evidence_refs": list(self.evidence_refs),
            "authority_refs": list(self.authority_refs),
            "timestamp": self.timestamp,
        }

    def digest(self) -> str:
        return content_digest(self.to_dict())


@dataclass(frozen=True)
class MutationReceipt:
    mutation_id: str
    idempotency_key: str
    prior_revision: int
    resulting_revision: int
    status: str
    mutation_digest: str
    replayed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "mutation_id": self.mutation_id,
            "idempotency_key": self.idempotency_key,
            "prior_revision": self.prior_revision,
            "resulting_revision": self.resulting_revision,
            "status": self.status,
            "mutation_digest": self.mutation_digest,
            "replayed": self.replayed,
        }


class GraphInvariantError(ValueError):
    """A mutation violated a deterministic graph invariant."""


class StaleGraphRevision(GraphInvariantError):
    """Mutation expected a graph revision other than the current revision."""


class MutationReplayConflict(GraphInvariantError):
    """An idempotency key was reused for different mutation content."""
