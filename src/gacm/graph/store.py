"""Deterministic governed graph state and mutation enforcement."""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Iterable

from .models import (
    EdgeType,
    EpistemicState,
    GraphEdge,
    GraphInvariantError,
    GraphMutation,
    GraphNode,
    MutationReceipt,
    MutationReplayConflict,
    ProducerRole,
    StaleGraphRevision,
)


_STATE_TRANSITIONS: dict[EpistemicState, frozenset[EpistemicState]] = {
    EpistemicState.UNKNOWN: frozenset({
        EpistemicState.UNKNOWN,
        EpistemicState.USER_STATED,
        EpistemicState.OBSERVED,
        EpistemicState.INFERRED,
        EpistemicState.HYPOTHESIS,
        EpistemicState.CONFLICTED,
        EpistemicState.EVIDENCED,
        EpistemicState.ACCEPTED,
        EpistemicState.SUPERSEDED,
    }),
    EpistemicState.USER_STATED: frozenset({
        EpistemicState.USER_STATED,
        EpistemicState.EVIDENCED,
        EpistemicState.CONFLICTED,
        EpistemicState.ACCEPTED,
        EpistemicState.SUPERSEDED,
    }),
    EpistemicState.OBSERVED: frozenset({
        EpistemicState.OBSERVED,
        EpistemicState.EVIDENCED,
        EpistemicState.CONFLICTED,
        EpistemicState.ACCEPTED,
        EpistemicState.SUPERSEDED,
    }),
    EpistemicState.INFERRED: frozenset({
        EpistemicState.INFERRED,
        EpistemicState.HYPOTHESIS,
        EpistemicState.EVIDENCED,
        EpistemicState.CONFLICTED,
        EpistemicState.ACCEPTED,
        EpistemicState.SUPERSEDED,
    }),
    EpistemicState.HYPOTHESIS: frozenset({
        EpistemicState.HYPOTHESIS,
        EpistemicState.INFERRED,
        EpistemicState.EVIDENCED,
        EpistemicState.CONFLICTED,
        EpistemicState.ACCEPTED,
        EpistemicState.SUPERSEDED,
    }),
    EpistemicState.EVIDENCED: frozenset({
        EpistemicState.EVIDENCED,
        EpistemicState.ACCEPTED,
        EpistemicState.CONFLICTED,
        EpistemicState.SUPERSEDED,
    }),
    EpistemicState.ACCEPTED: frozenset({
        EpistemicState.ACCEPTED,
        EpistemicState.CONFLICTED,
        EpistemicState.SUPERSEDED,
    }),
    EpistemicState.CONFLICTED: frozenset({
        EpistemicState.CONFLICTED,
        EpistemicState.EVIDENCED,
        EpistemicState.ACCEPTED,
        EpistemicState.SUPERSEDED,
    }),
    EpistemicState.SUPERSEDED: frozenset({EpistemicState.SUPERSEDED}),
}

_DISCOVERY_STATES = frozenset({
    EpistemicState.UNKNOWN,
    EpistemicState.INFERRED,
    EpistemicState.HYPOTHESIS,
})

_EXECUTOR_STATES = frozenset({
    EpistemicState.UNKNOWN,
    EpistemicState.OBSERVED,
    EpistemicState.INFERRED,
    EpistemicState.HYPOTHESIS,
    EpistemicState.CONFLICTED,
})

_ACCEPTING_ROLES = frozenset({
    ProducerRole.HUMAN,
    ProducerRole.GACM_GOVERNANCE,
    ProducerRole.RELEASE_AUTHORITY,
})

_EVIDENCING_ROLES = frozenset({
    ProducerRole.HUMAN,
    ProducerRole.GACM_GOVERNANCE,
    ProducerRole.INDEPENDENT_VERIFIER,
    ProducerRole.RELEASE_AUTHORITY,
    ProducerRole.SYSTEM,
})


class GovernedGraph:
    """In-process graph kernel.

    Storage is intentionally minimal in this tranche. The invariants and mutation
    contract are the authority boundary; a durable adapter can replace this store
    without changing them.
    """

    def __init__(self) -> None:
        self.revision = 0
        self._nodes: dict[str, GraphNode] = {}
        self._edges: dict[str, GraphEdge] = {}
        self._mutations: list[GraphMutation] = []
        self._mutation_receipts: list[MutationReceipt] = []
        self._idempotency: dict[str, tuple[str, MutationReceipt]] = {}

    @property
    def nodes(self) -> tuple[GraphNode, ...]:
        return tuple(self._nodes[key] for key in sorted(self._nodes))

    @property
    def edges(self) -> tuple[GraphEdge, ...]:
        return tuple(self._edges[key] for key in sorted(self._edges))

    @property
    def mutations(self) -> tuple[GraphMutation, ...]:
        return tuple(self._mutations)

    @property
    def mutation_receipts(self) -> tuple[MutationReceipt, ...]:
        return tuple(self._mutation_receipts)

    def node(self, object_id: str) -> GraphNode | None:
        return self._nodes.get(str(object_id))

    def edge(self, edge_id: str) -> GraphEdge | None:
        return self._edges.get(str(edge_id))

    def apply(self, mutation: GraphMutation) -> MutationReceipt:
        digest = mutation.digest()
        prior = self._idempotency.get(mutation.idempotency_key)
        if prior:
            prior_digest, prior_receipt = prior
            if prior_digest != digest:
                raise MutationReplayConflict(
                    f"idempotency key {mutation.idempotency_key!r} was reused with different content"
                )
            return MutationReceipt(
                mutation_id=prior_receipt.mutation_id,
                idempotency_key=prior_receipt.idempotency_key,
                prior_revision=prior_receipt.prior_revision,
                resulting_revision=prior_receipt.resulting_revision,
                status=prior_receipt.status,
                mutation_digest=prior_receipt.mutation_digest,
                replayed=True,
            )

        if mutation.expected_revision != self.revision:
            raise StaleGraphRevision(
                f"expected revision {mutation.expected_revision}, current revision is {self.revision}"
            )

        self._validate_mutation(mutation)
        prior_revision = self.revision
        for node in mutation.nodes:
            self._nodes[node.object_id] = node
        for edge in mutation.edges:
            self._edges[edge.edge_id] = edge
        self.revision += 1

        receipt = MutationReceipt(
            mutation_id=mutation.mutation_id,
            idempotency_key=mutation.idempotency_key,
            prior_revision=prior_revision,
            resulting_revision=self.revision,
            status="APPLIED",
            mutation_digest=digest,
        )
        self._mutations.append(mutation)
        self._mutation_receipts.append(receipt)
        self._idempotency[mutation.idempotency_key] = (digest, receipt)
        return receipt

    def _validate_mutation(self, mutation: GraphMutation) -> None:
        if not mutation.mutation_id.strip():
            raise GraphInvariantError("mutation_id is required")
        if not mutation.project_id.strip():
            raise GraphInvariantError("project_id is required")
        if not mutation.idempotency_key.strip():
            raise GraphInvariantError("idempotency_key is required")
        if not mutation.nodes and not mutation.edges:
            raise GraphInvariantError("empty graph mutation is not permitted")

        actor = self._role(mutation.actor_role)
        node_ids = [node.object_id for node in mutation.nodes]
        edge_ids = [edge.edge_id for edge in mutation.edges]
        if len(node_ids) != len(set(node_ids)):
            raise GraphInvariantError("duplicate node IDs in one mutation")
        if len(edge_ids) != len(set(edge_ids)):
            raise GraphInvariantError("duplicate edge IDs in one mutation")

        proposed_nodes = dict(self._nodes)
        for node in mutation.nodes:
            self._validate_node(node, mutation.project_id, actor)
            existing = self._nodes.get(node.object_id)
            if existing:
                self._validate_node_update(existing, node)
            proposed_nodes[node.object_id] = node

        for edge in mutation.edges:
            self._validate_edge(edge, mutation.project_id, actor, proposed_nodes)
            existing = self._edges.get(edge.edge_id)
            if existing:
                self._validate_edge_update(existing, edge)

    def _validate_node(self, node: GraphNode, project_id: str, actor: ProducerRole) -> None:
        if not node.object_id.strip():
            raise GraphInvariantError("node object_id is required")
        if node.project_id != project_id:
            raise GraphInvariantError("node project scope differs from mutation project")
        self._validate_metadata(
            created_at=node.created_at,
            confidence=node.confidence,
            schema_version=node.schema_version,
            superseded_by=node.superseded_by,
            state=node.epistemic_state,
        )
        self._validate_common(
            state=node.epistemic_state,
            source=node.source,
            provenance=node.provenance,
            authority_ref=node.authority_ref,
            authority_digest=node.authority_digest,
            producer_role=node.producer_role,
            actor=actor,
        )

    def _validate_edge(
        self,
        edge: GraphEdge,
        project_id: str,
        actor: ProducerRole,
        proposed_nodes: dict[str, GraphNode],
    ) -> None:
        if not edge.edge_id.strip():
            raise GraphInvariantError("edge edge_id is required")
        if edge.project_id != project_id:
            raise GraphInvariantError("edge project scope differs from mutation project")
        if edge.from_id == edge.to_id:
            raise GraphInvariantError("self-referential graph edges are not permitted")
        if edge.from_id not in proposed_nodes or edge.to_id not in proposed_nodes:
            raise GraphInvariantError("edge endpoint does not exist")
        if proposed_nodes[edge.from_id].project_id != project_id or proposed_nodes[edge.to_id].project_id != project_id:
            raise GraphInvariantError("cross-project graph edges are not permitted")
        try:
            EdgeType(str(edge.relationship))
        except ValueError as exc:
            raise GraphInvariantError(f"unknown relationship type: {edge.relationship}") from exc
        self._validate_metadata(
            created_at=edge.created_at,
            confidence=edge.confidence,
            schema_version=edge.schema_version,
            superseded_by=edge.superseded_by,
            state=edge.epistemic_state,
        )
        self._validate_common(
            state=edge.epistemic_state,
            source=edge.source,
            provenance=edge.provenance,
            authority_ref=edge.authority_ref,
            authority_digest=edge.authority_digest,
            producer_role=edge.producer_role,
            actor=actor,
        )

    def _validate_common(
        self,
        *,
        state: EpistemicState | str,
        source: str,
        provenance: tuple[str, ...],
        authority_ref: str | None,
        authority_digest: str | None,
        producer_role: ProducerRole | str,
        actor: ProducerRole,
    ) -> None:
        try:
            epistemic = EpistemicState(str(state))
        except ValueError as exc:
            raise GraphInvariantError(f"unknown epistemic state: {state}") from exc
        producer = self._role(producer_role)
        if producer != actor:
            raise GraphInvariantError("producer role must match authenticated mutation actor")
        if not source.strip():
            raise GraphInvariantError("source is required")
        if not provenance:
            raise GraphInvariantError("provenance is required")
        if epistemic in {EpistemicState.EVIDENCED, EpistemicState.ACCEPTED}:
            if not authority_ref or not authority_digest:
                raise GraphInvariantError("evidenced/accepted graph objects require authority reference and digest")
        if actor == ProducerRole.DISCOVERY and epistemic not in _DISCOVERY_STATES:
            raise GraphInvariantError("discovery may only write candidate/non-authoritative graph states")
        if actor == ProducerRole.EXECUTOR and epistemic not in _EXECUTOR_STATES:
            raise GraphInvariantError("executor may not write evidenced or accepted graph authority")
        if epistemic == EpistemicState.ACCEPTED and actor not in _ACCEPTING_ROLES:
            raise GraphInvariantError("only governed human/release authority may accept graph truth")
        if epistemic == EpistemicState.EVIDENCED and actor not in _EVIDENCING_ROLES:
            raise GraphInvariantError("actor is not authorized to write evidenced graph truth")

    @staticmethod
    def _validate_metadata(
        *,
        created_at: str,
        confidence: float | None,
        schema_version: str,
        superseded_by: str | None,
        state: EpistemicState | str,
    ) -> None:
        if not created_at.strip():
            raise GraphInvariantError("created_at is required")
        if not schema_version.strip():
            raise GraphInvariantError("schema_version is required")
        if confidence is not None and not 0 <= float(confidence) <= 1:
            raise GraphInvariantError("confidence must be between 0 and 1")
        if EpistemicState(str(state)) == EpistemicState.SUPERSEDED and not superseded_by:
            raise GraphInvariantError("superseded graph objects require superseded_by")

    def _validate_node_update(self, old: GraphNode, new: GraphNode) -> None:
        if (
            old.project_id != new.project_id
            or old.organization_id != new.organization_id
            or old.run_id != new.run_id
            or str(old.object_type) != str(new.object_type)
        ):
            raise GraphInvariantError("node identity/scope/type is immutable")
        self._validate_transition(old.epistemic_state, new.epistemic_state)

    def _validate_edge_update(self, old: GraphEdge, new: GraphEdge) -> None:
        if (
            old.project_id != new.project_id
            or old.organization_id != new.organization_id
            or old.run_id != new.run_id
            or str(old.relationship) != str(new.relationship)
            or old.from_id != new.from_id
            or old.to_id != new.to_id
        ):
            raise GraphInvariantError("edge identity/scope/endpoints/relationship are immutable")
        self._validate_transition(old.epistemic_state, new.epistemic_state)

    @staticmethod
    def _validate_transition(old: EpistemicState | str, new: EpistemicState | str) -> None:
        old_state = EpistemicState(str(old))
        new_state = EpistemicState(str(new))
        if new_state not in _STATE_TRANSITIONS[old_state]:
            raise GraphInvariantError(f"illegal epistemic transition {old_state} -> {new_state}")

    @staticmethod
    def _role(value: ProducerRole | str) -> ProducerRole:
        try:
            return ProducerRole(str(value))
        except ValueError as exc:
            raise GraphInvariantError(f"unknown producer role: {value}") from exc

    def outgoing(self, object_id: str, relationships: Iterable[EdgeType | str] = ()) -> tuple[GraphEdge, ...]:
        allowed = {str(item) for item in relationships}
        return tuple(
            edge
            for edge in self.edges
            if edge.from_id == object_id and (not allowed or str(edge.relationship) in allowed)
        )

    def incoming(self, object_id: str, relationships: Iterable[EdgeType | str] = ()) -> tuple[GraphEdge, ...]:
        allowed = {str(item) for item in relationships}
        return tuple(
            edge
            for edge in self.edges
            if edge.to_id == object_id and (not allowed or str(edge.relationship) in allowed)
        )

    def transitive_dependents(self, object_ids: Iterable[str]) -> tuple[str, ...]:
        reverse: dict[str, set[str]] = defaultdict(set)
        for edge in self.edges:
            if str(edge.relationship) == EdgeType.DEPENDS_ON:
                reverse[edge.to_id].add(edge.from_id)
        seen: set[str] = set()
        queue = deque(sorted(str(item) for item in object_ids))
        while queue:
            parent = queue.popleft()
            for child in sorted(reverse.get(parent, ())):
                if child not in seen:
                    seen.add(child)
                    queue.append(child)
        return tuple(sorted(seen))

    def snapshot(self, *, project_id: str | None = None) -> dict:
        nodes = [node.to_dict() for node in self.nodes if project_id is None or node.project_id == project_id]
        node_ids = {node["object_id"] for node in nodes}
        edges = [
            edge.to_dict()
            for edge in self.edges
            if edge.from_id in node_ids and edge.to_id in node_ids
        ]
        return {
            "revision": self.revision,
            "project_id": project_id,
            "nodes": nodes,
            "edges": edges,
            "mutation_history": [item.to_dict() for item in self.mutations],
            "mutation_receipts": [item.to_dict() for item in self.mutation_receipts],
        }
