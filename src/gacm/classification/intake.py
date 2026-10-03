"""Jev-to-governed-graph intake adapter.

The adapter may record only non-authoritative inferred candidates. The graph
scheduler must obtain stronger evidence before those candidates can govern work.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from gacm.graph.models import GraphMutation, MutationReceipt, ProducerRole
from gacm.graph.store import GovernedGraph

from .jev import JevClassificationResult, JevClient
from .taxonomy import (
    GACM_INPUT_KIND_QUESTION,
    GACM_INPUT_KIND_TITLES,
    graph_node_type,
)


@dataclass(frozen=True)
class JevIntakeReceipt:
    classification: JevClassificationResult
    graph_receipt: MutationReceipt
    object_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "classification": self.classification.to_dict(),
            "graph_receipt": self.graph_receipt.to_dict(),
            "object_id": self.object_id,
            "authoritative": False,
        }


class JevGraphIntake:
    """Classify raw state and record one inferred candidate in the governed graph."""

    def __init__(self, client: JevClient):
        self.client = client

    def classify_and_record(
        self,
        graph: GovernedGraph,
        *,
        state: Any,
        project_id: str,
        source_snapshot_id: str,
        created_at: str,
        run_id: str | None = None,
    ) -> JevIntakeReceipt:
        classification = self.client.classify(
            state=state,
            questions={"input_kind": GACM_INPUT_KIND_QUESTION},
        )
        code, _, _ = classification.choice("input_kind")
        identity_material = (
            f"{project_id}|{run_id or ''}|{source_snapshot_id}|"
            f"{classification.result_digest}|{code}"
        )
        short = hashlib.sha256(identity_material.encode("utf-8")).hexdigest()[:20]
        object_id = f"jev-candidate-{short}"
        node = classification.propose_graph_node(
            question_name="input_kind",
            taxonomy_titles=GACM_INPUT_KIND_TITLES,
            object_id=object_id,
            project_id=project_id,
            object_type=graph_node_type(code),
            created_at=created_at,
            source_snapshot_id=source_snapshot_id,
            run_id=run_id,
        )
        mutation = GraphMutation(
            mutation_id=f"jev-mutation-{short}",
            project_id=project_id,
            expected_revision=graph.revision,
            actor_role=ProducerRole.ORCHESTRATION,
            idempotency_key=f"jev:{classification.result_digest}",
            nodes=(node,),
            rationale="Record advisory Jev classification for governed evidence collection.",
            timestamp=created_at,
        )
        graph_receipt = graph.apply(mutation)
        return JevIntakeReceipt(
            classification=classification,
            graph_receipt=graph_receipt,
            object_id=object_id,
        )
