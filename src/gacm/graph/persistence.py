"""Durable, replay-validated persistence for the governed GACM graph."""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .models import (
    GraphEdge,
    GraphMutation,
    GraphNode,
    MutationReceipt,
    content_digest,
)
from .store import GovernedGraph


GRAPH_STORE_FORMAT = "GACM_GOVERNED_GRAPH_STORE"
GRAPH_STORE_SCHEMA_VERSION = "1.0.0"


class GraphPersistenceError(RuntimeError):
    """Durable graph state is unavailable, malformed, stale, or inconsistent."""


class GraphPersistenceIntegrityError(GraphPersistenceError):
    """Persisted graph bytes do not reconstruct to the claimed governed state."""


class StalePersistedGraphRevision(GraphPersistenceError):
    """A writer attempted to replace a durable graph from a stale base revision."""


class GraphPersistenceLocked(GraphPersistenceError):
    """Another process currently owns the durable graph writer lock."""


@dataclass(frozen=True)
class GraphPersistenceReceipt:
    path: str
    prior_persisted_revision: int | None
    persisted_revision: int
    payload_digest: str
    status: str = "PERSISTED"

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "prior_persisted_revision": self.prior_persisted_revision,
            "persisted_revision": self.persisted_revision,
            "payload_digest": self.payload_digest,
            "status": self.status,
        }


class JsonGovernedGraphStore:
    """Atomic JSON persistence that reconstructs authority by mutation replay."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def exists(self) -> bool:
        return self.path.is_file()

    def save(
        self,
        graph: GovernedGraph,
        *,
        expected_stored_revision: int | None,
    ) -> GraphPersistenceReceipt:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._exclusive_writer():
            return self._save_locked(
                graph,
                expected_stored_revision=expected_stored_revision,
            )

    def apply(
        self,
        mutation: GraphMutation,
    ) -> tuple[MutationReceipt, GraphPersistenceReceipt]:
        """Apply one governed mutation and durably commit it under one writer lock."""

        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._exclusive_writer():
            if self.path.exists():
                graph, _ = self._load_validated()
                prior_revision: int | None = graph.revision
            else:
                graph = GovernedGraph()
                prior_revision = None
            mutation_receipt = graph.apply(mutation)
            persistence_receipt = self._save_locked(
                graph,
                expected_stored_revision=prior_revision,
            )
            return mutation_receipt, persistence_receipt

    def _save_locked(
        self,
        graph: GovernedGraph,
        *,
        expected_stored_revision: int | None,
    ) -> GraphPersistenceReceipt:
        snapshot = graph.snapshot()
        if snapshot.get("project_id") is not None:
            raise GraphPersistenceError(
                "durable graph store requires a complete unfiltered snapshot"
            )

        prior_revision: int | None = None
        prior_snapshot: Mapping[str, Any] | None = None
        if self.path.exists():
            prior_graph, prior_record = self._load_validated()
            prior_revision = prior_graph.revision
            prior_snapshot = prior_record["graph"]
            if expected_stored_revision is None or expected_stored_revision != prior_revision:
                raise StalePersistedGraphRevision(
                    f"expected stored revision {expected_stored_revision}, current durable revision is {prior_revision}"
                )
            self._validate_history_extension(prior_snapshot, snapshot)
        elif expected_stored_revision is not None:
            raise StalePersistedGraphRevision(
                f"expected stored revision {expected_stored_revision}, but durable graph does not exist"
            )

        payload = {
            "format": GRAPH_STORE_FORMAT,
            "schema_version": GRAPH_STORE_SCHEMA_VERSION,
            "graph": snapshot,
        }
        digest = content_digest(payload)
        record = {**payload, "payload_digest": digest}

        if prior_snapshot is not None and graph.revision == prior_revision:
            prior_payload = {
                "format": GRAPH_STORE_FORMAT,
                "schema_version": GRAPH_STORE_SCHEMA_VERSION,
                "graph": prior_snapshot,
            }
            if content_digest(prior_payload) != digest:
                raise StalePersistedGraphRevision(
                    "same durable revision cannot be replaced with different graph content"
                )

        # Do not persist even an in-memory candidate unless normal governed replay
        # reconstructs the exact projection and receipts.
        self._reconstruct_record(record)

        try:
            serialized = json.dumps(
                record,
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
            ) + "\n"
        except (TypeError, ValueError) as error:
            raise GraphPersistenceIntegrityError(
                "graph snapshot is not JSON serializable"
            ) from error

        temp = self.path.with_name(f".{self.path.name}.{os.getpid()}.tmp")
        try:
            with temp.open("w", encoding="utf-8", newline="\n") as handle:
                handle.write(serialized)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp, self.path)
            self._fsync_parent_best_effort()
        finally:
            if temp.exists():
                temp.unlink()

        return GraphPersistenceReceipt(
            path=str(self.path),
            prior_persisted_revision=prior_revision,
            persisted_revision=graph.revision,
            payload_digest=digest,
        )

    @contextmanager
    def _exclusive_writer(self):
        lock_path = self.path.with_name(f".{self.path.name}.lock")
        with lock_path.open("a+b") as handle:
            handle.seek(0, os.SEEK_END)
            if handle.tell() == 0:
                handle.write(b"0")
                handle.flush()
            handle.seek(0)
            try:
                if os.name == "nt":
                    import msvcrt

                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as error:
                raise GraphPersistenceLocked(
                    f"durable graph writer lock is already held: {lock_path}"
                ) from error
            try:
                yield
            finally:
                handle.seek(0)
                if os.name == "nt":
                    import msvcrt

                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def _fsync_parent_best_effort(self) -> None:
        try:
            descriptor = os.open(str(self.path.parent), os.O_RDONLY)
        except OSError:
            return
        try:
            os.fsync(descriptor)
        except OSError:
            pass
        finally:
            os.close(descriptor)

    def load(self) -> GovernedGraph:
        graph, _ = self._load_validated()
        return graph

    def inspect(self) -> dict[str, Any]:
        graph, record = self._load_validated()
        return {
            "path": str(self.path),
            "format": record["format"],
            "schema_version": record["schema_version"],
            "revision": graph.revision,
            "payload_digest": record["payload_digest"],
            "mutation_count": len(graph.mutations),
            "node_count": len(graph.nodes),
            "edge_count": len(graph.edges),
        }

    def _load_validated(self) -> tuple[GovernedGraph, Mapping[str, Any]]:
        record = self._read_record()
        return self._reconstruct_record(record), record

    def _reconstruct_record(self, record: Mapping[str, Any]) -> GovernedGraph:
        graph_snapshot = self._mapping(record["graph"], "graph")
        mutations_raw = graph_snapshot["mutation_history"]
        receipts_raw = graph_snapshot["mutation_receipts"]

        if len(mutations_raw) != len(receipts_raw):
            raise GraphPersistenceIntegrityError(
                "mutation history and receipt counts differ"
            )

        graph = GovernedGraph()
        reconstructed_receipts: list[dict[str, Any]] = []
        for index, raw_mutation in enumerate(mutations_raw):
            mutation = self._mutation_from_dict(raw_mutation)
            if mutation.expected_revision != index:
                raise GraphPersistenceIntegrityError(
                    "mutation history revision sequence is not contiguous"
                )
            try:
                receipt = graph.apply(mutation)
            except Exception as error:
                raise GraphPersistenceIntegrityError(
                    f"persisted mutation {mutation.mutation_id!r} failed governed replay"
                ) from error
            reconstructed_receipts.append(receipt.to_dict())

        persisted_revision = self._strict_int(
            graph_snapshot["revision"], "graph.revision"
        )
        if graph.revision != persisted_revision:
            raise GraphPersistenceIntegrityError(
                f"replayed revision {graph.revision} differs from persisted revision {persisted_revision}"
            )

        parsed_receipts = [
            self._receipt_from_dict(item).to_dict() for item in receipts_raw
        ]
        if reconstructed_receipts != parsed_receipts:
            raise GraphPersistenceIntegrityError(
                "persisted mutation receipts differ from governed replay receipts"
            )

        reconstructed = graph.snapshot()
        if reconstructed != graph_snapshot:
            raise GraphPersistenceIntegrityError(
                "persisted graph projection differs from governed replay projection"
            )
        return graph

    def _read_record(self) -> Mapping[str, Any]:
        if not self.path.is_file():
            raise GraphPersistenceError(f"durable graph file does not exist: {self.path}")
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise GraphPersistenceIntegrityError(
                "durable graph file is unreadable or malformed"
            ) from error
        record = self._mapping(raw, "record")
        self._exact_keys(
            record,
            {"format", "schema_version", "graph", "payload_digest"},
            "record",
        )
        if record["format"] != GRAPH_STORE_FORMAT:
            raise GraphPersistenceIntegrityError("unsupported graph store format")
        if record["schema_version"] != GRAPH_STORE_SCHEMA_VERSION:
            raise GraphPersistenceIntegrityError("unsupported graph store schema version")
        if not isinstance(record["payload_digest"], str) or not record["payload_digest"]:
            raise GraphPersistenceIntegrityError("payload_digest must be a non-empty string")

        graph = self._mapping(record["graph"], "graph")
        self._exact_keys(
            graph,
            {
                "revision",
                "project_id",
                "nodes",
                "edges",
                "mutation_history",
                "mutation_receipts",
            },
            "graph",
        )
        if graph["project_id"] is not None:
            raise GraphPersistenceIntegrityError(
                "durable graph record must contain the complete graph, not a project-filtered snapshot"
            )
        self._strict_int(graph["revision"], "graph.revision")
        for name in ("nodes", "edges", "mutation_history", "mutation_receipts"):
            if not isinstance(graph[name], list):
                raise GraphPersistenceIntegrityError(f"graph.{name} must be an array")

        payload = {
            "format": record["format"],
            "schema_version": record["schema_version"],
            "graph": graph,
        }
        calculated = content_digest(payload)
        if calculated != record["payload_digest"]:
            raise GraphPersistenceIntegrityError("durable graph payload digest mismatch")
        return record

    @classmethod
    def _mutation_from_dict(cls, raw: Any) -> GraphMutation:
        item = cls._mapping(raw, "mutation")
        cls._exact_keys(
            item,
            {
                "mutation_id",
                "project_id",
                "expected_revision",
                "actor_role",
                "idempotency_key",
                "nodes",
                "edges",
                "rationale",
                "evidence_refs",
                "authority_refs",
                "timestamp",
            },
            "mutation",
        )
        cls._strings(
            item,
            (
                "mutation_id",
                "project_id",
                "actor_role",
                "idempotency_key",
                "rationale",
                "timestamp",
            ),
            "mutation",
        )
        expected_revision = cls._strict_int(
            item["expected_revision"], "mutation.expected_revision"
        )
        nodes = cls._list(item["nodes"], "mutation.nodes")
        edges = cls._list(item["edges"], "mutation.edges")
        evidence_refs = cls._string_list(
            item["evidence_refs"], "mutation.evidence_refs"
        )
        authority_refs = cls._string_list(
            item["authority_refs"], "mutation.authority_refs"
        )
        return GraphMutation(
            mutation_id=item["mutation_id"],
            project_id=item["project_id"],
            expected_revision=expected_revision,
            actor_role=item["actor_role"],
            idempotency_key=item["idempotency_key"],
            nodes=tuple(cls._node_from_dict(node) for node in nodes),
            edges=tuple(cls._edge_from_dict(edge) for edge in edges),
            rationale=item["rationale"],
            evidence_refs=evidence_refs,
            authority_refs=authority_refs,
            timestamp=item["timestamp"],
        )

    @classmethod
    def _node_from_dict(cls, raw: Any) -> GraphNode:
        item = cls._mapping(raw, "node")
        keys = {
            "object_id",
            "project_id",
            "organization_id",
            "run_id",
            "object_type",
            "epistemic_state",
            "status",
            "source",
            "source_snapshot_id",
            "provenance",
            "authority_ref",
            "authority_digest",
            "producer_role",
            "verification_state",
            "confidence",
            "created_at",
            "valid_from",
            "valid_to",
            "superseded_by",
            "schema_version",
            "payload",
        }
        cls._exact_keys(item, keys, "node")
        cls._strings(
            item,
            (
                "object_id",
                "project_id",
                "object_type",
                "epistemic_state",
                "status",
                "source",
                "producer_role",
                "verification_state",
                "created_at",
                "schema_version",
            ),
            "node",
        )
        for key in (
            "organization_id",
            "run_id",
            "source_snapshot_id",
            "authority_ref",
            "authority_digest",
            "valid_from",
            "valid_to",
            "superseded_by",
        ):
            cls._optional_string(item[key], f"node.{key}")
        confidence = item["confidence"]
        if confidence is not None and (
            isinstance(confidence, bool) or not isinstance(confidence, (int, float))
        ):
            raise GraphPersistenceIntegrityError("node.confidence must be numeric or null")
        payload = cls._mapping(item["payload"], "node.payload")
        return GraphNode(
            object_id=item["object_id"],
            project_id=item["project_id"],
            organization_id=item["organization_id"],
            run_id=item["run_id"],
            object_type=item["object_type"],
            epistemic_state=item["epistemic_state"],
            status=item["status"],
            source=item["source"],
            source_snapshot_id=item["source_snapshot_id"],
            provenance=cls._string_list(item["provenance"], "node.provenance"),
            authority_ref=item["authority_ref"],
            authority_digest=item["authority_digest"],
            producer_role=item["producer_role"],
            verification_state=item["verification_state"],
            confidence=confidence,
            created_at=item["created_at"],
            valid_from=item["valid_from"],
            valid_to=item["valid_to"],
            superseded_by=item["superseded_by"],
            schema_version=item["schema_version"],
            payload=dict(payload),
        )

    @classmethod
    def _edge_from_dict(cls, raw: Any) -> GraphEdge:
        item = cls._mapping(raw, "edge")
        keys = {
            "edge_id",
            "project_id",
            "organization_id",
            "run_id",
            "relationship",
            "from_id",
            "to_id",
            "epistemic_state",
            "source",
            "source_snapshot_id",
            "provenance",
            "authority_ref",
            "authority_digest",
            "producer_role",
            "verification_state",
            "confidence",
            "created_at",
            "valid_from",
            "valid_to",
            "superseded_by",
            "schema_version",
            "payload",
        }
        cls._exact_keys(item, keys, "edge")
        cls._strings(
            item,
            (
                "edge_id",
                "project_id",
                "relationship",
                "from_id",
                "to_id",
                "epistemic_state",
                "source",
                "producer_role",
                "verification_state",
                "created_at",
                "schema_version",
            ),
            "edge",
        )
        for key in (
            "organization_id",
            "run_id",
            "source_snapshot_id",
            "authority_ref",
            "authority_digest",
            "valid_from",
            "valid_to",
            "superseded_by",
        ):
            cls._optional_string(item[key], f"edge.{key}")
        confidence = item["confidence"]
        if confidence is not None and (
            isinstance(confidence, bool) or not isinstance(confidence, (int, float))
        ):
            raise GraphPersistenceIntegrityError("edge.confidence must be numeric or null")
        payload = cls._mapping(item["payload"], "edge.payload")
        return GraphEdge(
            edge_id=item["edge_id"],
            project_id=item["project_id"],
            organization_id=item["organization_id"],
            run_id=item["run_id"],
            relationship=item["relationship"],
            from_id=item["from_id"],
            to_id=item["to_id"],
            epistemic_state=item["epistemic_state"],
            source=item["source"],
            source_snapshot_id=item["source_snapshot_id"],
            provenance=cls._string_list(item["provenance"], "edge.provenance"),
            authority_ref=item["authority_ref"],
            authority_digest=item["authority_digest"],
            producer_role=item["producer_role"],
            verification_state=item["verification_state"],
            confidence=confidence,
            created_at=item["created_at"],
            valid_from=item["valid_from"],
            valid_to=item["valid_to"],
            superseded_by=item["superseded_by"],
            schema_version=item["schema_version"],
            payload=dict(payload),
        )

    @classmethod
    def _receipt_from_dict(cls, raw: Any) -> MutationReceipt:
        item = cls._mapping(raw, "mutation_receipt")
        cls._exact_keys(
            item,
            {
                "mutation_id",
                "idempotency_key",
                "prior_revision",
                "resulting_revision",
                "status",
                "mutation_digest",
                "replayed",
            },
            "mutation_receipt",
        )
        cls._strings(
            item,
            ("mutation_id", "idempotency_key", "status", "mutation_digest"),
            "mutation_receipt",
        )
        if not isinstance(item["replayed"], bool):
            raise GraphPersistenceIntegrityError(
                "mutation_receipt.replayed must be boolean"
            )
        return MutationReceipt(
            mutation_id=item["mutation_id"],
            idempotency_key=item["idempotency_key"],
            prior_revision=cls._strict_int(
                item["prior_revision"], "mutation_receipt.prior_revision"
            ),
            resulting_revision=cls._strict_int(
                item["resulting_revision"], "mutation_receipt.resulting_revision"
            ),
            status=item["status"],
            mutation_digest=item["mutation_digest"],
            replayed=item["replayed"],
        )

    @staticmethod
    def _validate_history_extension(
        prior: Mapping[str, Any],
        candidate: Mapping[str, Any],
    ) -> None:
        prior_revision = prior["revision"]
        candidate_revision = candidate["revision"]
        if candidate_revision < prior_revision:
            raise StalePersistedGraphRevision(
                "candidate graph revision is older than durable graph revision"
            )
        prior_history = prior["mutation_history"]
        candidate_history = candidate["mutation_history"]
        prior_receipts = prior["mutation_receipts"]
        candidate_receipts = candidate["mutation_receipts"]
        if candidate_history[: len(prior_history)] != prior_history:
            raise StalePersistedGraphRevision(
                "candidate mutation history does not extend durable history"
            )
        if candidate_receipts[: len(prior_receipts)] != prior_receipts:
            raise StalePersistedGraphRevision(
                "candidate mutation receipts do not extend durable receipts"
            )

    @staticmethod
    def _mapping(value: Any, name: str) -> Mapping[str, Any]:
        if not isinstance(value, Mapping):
            raise GraphPersistenceIntegrityError(f"{name} must be an object")
        return value

    @staticmethod
    def _list(value: Any, name: str) -> list[Any]:
        if not isinstance(value, list):
            raise GraphPersistenceIntegrityError(f"{name} must be an array")
        return value

    @classmethod
    def _string_list(cls, value: Any, name: str) -> tuple[str, ...]:
        items = cls._list(value, name)
        if any(not isinstance(item, str) for item in items):
            raise GraphPersistenceIntegrityError(f"{name} must contain only strings")
        return tuple(items)

    @staticmethod
    def _strict_int(value: Any, name: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise GraphPersistenceIntegrityError(
                f"{name} must be a non-negative integer"
            )
        return value

    @staticmethod
    def _optional_string(value: Any, name: str) -> None:
        if value is not None and not isinstance(value, str):
            raise GraphPersistenceIntegrityError(f"{name} must be a string or null")

    @staticmethod
    def _strings(item: Mapping[str, Any], keys: tuple[str, ...], name: str) -> None:
        for key in keys:
            if not isinstance(item[key], str):
                raise GraphPersistenceIntegrityError(f"{name}.{key} must be a string")

    @staticmethod
    def _exact_keys(item: Mapping[str, Any], expected: set[str], name: str) -> None:
        actual = set(item)
        if actual != expected:
            missing = sorted(expected - actual)
            extra = sorted(actual - expected)
            raise GraphPersistenceIntegrityError(
                f"{name} keys differ; missing={missing}, extra={extra}"
            )
