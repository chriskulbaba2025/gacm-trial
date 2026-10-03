import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gacm.graph import (  # noqa: E402
    EdgeType,
    EpistemicState,
    GovernedGraph,
    GraphEdge,
    GraphMutation,
    GraphNode,
    GraphPersistenceError,
    GraphPersistenceIntegrityError,
    GraphPersistenceLocked,
    GraphScheduler,
    JsonGovernedGraphStore,
    MutationReceipt,
    NodeType,
    ProducerRole,
    StalePersistedGraphRevision,
)
from gacm.graph.models import content_digest  # noqa: E402


PROJECT = "persistence-test"


def tranche_node():
    return GraphNode(
        object_id="tranche-1",
        project_id=PROJECT,
        run_id="run-persist",
        object_type=NodeType.TRANCHE,
        epistemic_state=EpistemicState.OBSERVED,
        status="READY",
        source="test",
        source_snapshot_id="snapshot-1",
        provenance=("test:evidence",),
        producer_role=ProducerRole.ORCHESTRATION,
        verification_state="NOT_VERIFIED",
        created_at="2026-10-03T23:00:00Z",
        payload={
            "work_unit_id": "persist-u1",
            "task_objective": "prove durable graph reconstruction",
            "allowed_surfaces": ["src/gacm/graph/"],
            "forbidden_surfaces": ["production"],
            "test_contract": ["persistence"],
            "stop_conditions": ["scope change"],
            "external_action_required": False,
        },
    )


def risk_node(
    state=EpistemicState.INFERRED,
    status="OPEN",
    *,
    role=ProducerRole.ORCHESTRATION,
    authority=False,
):
    return GraphNode(
        object_id="risk-1",
        project_id=PROJECT,
        run_id="run-persist",
        object_type=NodeType.RISK,
        epistemic_state=state,
        status=status,
        source="test",
        source_snapshot_id="snapshot-1",
        provenance=("test:evidence",),
        authority_ref="authority:test" if authority else None,
        authority_digest="a" * 64 if authority else None,
        producer_role=role,
        verification_state="VERIFIED" if authority else "NOT_VERIFIED",
        created_at="2026-10-03T23:00:00Z",
        payload={"title": "Durability risk"},
    )


def blocking_edge():
    return GraphEdge(
        edge_id="edge-tranche-risk",
        project_id=PROJECT,
        run_id="run-persist",
        relationship=EdgeType.BLOCKED_BY,
        from_id="tranche-1",
        to_id="risk-1",
        epistemic_state=EpistemicState.OBSERVED,
        source="test",
        source_snapshot_id="snapshot-1",
        provenance=("test:evidence",),
        producer_role=ProducerRole.ORCHESTRATION,
        verification_state="NOT_VERIFIED",
        created_at="2026-10-03T23:00:00Z",
    )


def mutation_one():
    return GraphMutation(
        mutation_id="persist-m1",
        project_id=PROJECT,
        expected_revision=0,
        actor_role=ProducerRole.ORCHESTRATION,
        idempotency_key="persist-key-1",
        nodes=(tranche_node(), risk_node()),
        edges=(blocking_edge(),),
        rationale="create graph with unresolved blocker",
        evidence_refs=("test:evidence",),
        timestamp="2026-10-03T23:00:00Z",
    )


def mutation_two():
    return GraphMutation(
        mutation_id="persist-m2",
        project_id=PROJECT,
        expected_revision=1,
        actor_role=ProducerRole.INDEPENDENT_VERIFIER,
        idempotency_key="persist-key-2",
        nodes=(
            risk_node(
                EpistemicState.EVIDENCED,
                "RESOLVED",
                role=ProducerRole.INDEPENDENT_VERIFIER,
                authority=True,
            ),
        ),
        rationale="verify blocker resolved",
        evidence_refs=("verification:risk",),
        authority_refs=("authority:test",),
        timestamp="2026-10-03T23:01:00Z",
    )


def build_graph():
    graph = GovernedGraph()
    graph.apply(mutation_one())
    graph.apply(mutation_two())
    return graph


def recompute_record_digest(record):
    payload = {
        "format": record["format"],
        "schema_version": record["schema_version"],
        "graph": record["graph"],
    }
    record["payload_digest"] = content_digest(payload)


class GraphPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "graph-state.json"
        self.store = JsonGovernedGraphStore(self.path)

    def save_graph(self):
        graph = build_graph()
        receipt = self.store.save(graph, expected_stored_revision=None)
        self.assertEqual(2, receipt.persisted_revision)
        self.assertIsNone(receipt.prior_persisted_revision)
        return graph

    def read_record(self):
        return json.loads(self.path.read_text(encoding="utf-8"))

    def write_record(self, record):
        self.path.write_text(
            json.dumps(record, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def test_save_load_replays_exact_graph_and_scheduler_output(self):
        original = self.save_graph()
        original_actions = [
            action.to_dict()
            for action in GraphScheduler(original).next_actions(PROJECT, run_id="run-persist")
        ]

        loaded = JsonGovernedGraphStore(self.path).load()
        loaded_actions = [
            action.to_dict()
            for action in GraphScheduler(loaded).next_actions(PROJECT, run_id="run-persist")
        ]

        self.assertEqual(original.snapshot(), loaded.snapshot())
        self.assertEqual(2, loaded.revision)
        self.assertEqual(original_actions, loaded_actions)
        self.assertEqual(["EXECUTE_TRANCHE"], [item["kind"] for item in loaded_actions])

    def test_real_new_python_process_reconstructs_same_graph(self):
        original = self.save_graph()
        expected_snapshot_digest = content_digest(original.snapshot())
        code = (
            "import json,sys;"
            "from gacm.graph import JsonGovernedGraphStore,GraphScheduler;"
            "from gacm.graph.models import content_digest;"
            "g=JsonGovernedGraphStore(sys.argv[1]).load();"
            "a=GraphScheduler(g).next_actions('persistence-test',run_id='run-persist');"
            "print(json.dumps({'revision':g.revision,'snapshot_digest':content_digest(g.snapshot()),"
            "'actions':[x.to_dict() for x in a]},sort_keys=True))"
        )
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        completed = subprocess.run(
            [sys.executable, "-B", "-c", code, str(self.path)],
            cwd=str(ROOT),
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        restarted = json.loads(completed.stdout)
        self.assertEqual(2, restarted["revision"])
        self.assertEqual(expected_snapshot_digest, restarted["snapshot_digest"])
        self.assertEqual(["EXECUTE_TRANCHE"], [item["kind"] for item in restarted["actions"]])

    def test_idempotency_state_is_rebuilt_by_replay(self):
        self.save_graph()
        loaded = self.store.load()

        replay = loaded.apply(mutation_one())

        self.assertTrue(replay.replayed)
        self.assertEqual(2, loaded.revision)
        self.assertEqual(2, len(loaded.mutations))

    def test_reconstructed_graph_accepts_next_mutation_and_persists_extension(self):
        self.save_graph()
        loaded = self.store.load()
        next_node = GraphNode(
            object_id="evidence-2",
            project_id=PROJECT,
            run_id="run-persist",
            object_type=NodeType.EVIDENCE,
            epistemic_state=EpistemicState.OBSERVED,
            status="RECORDED",
            source="test",
            provenance=("test:evidence-2",),
            producer_role=ProducerRole.ORCHESTRATION,
            created_at="2026-10-03T23:02:00Z",
        )
        loaded.apply(
            GraphMutation(
                mutation_id="persist-m3",
                project_id=PROJECT,
                expected_revision=2,
                actor_role=ProducerRole.ORCHESTRATION,
                idempotency_key="persist-key-3",
                nodes=(next_node,),
                rationale="continue reconstructed graph",
                evidence_refs=("test:evidence-2",),
                timestamp="2026-10-03T23:02:00Z",
            )
        )

        receipt = self.store.save(loaded, expected_stored_revision=2)
        reloaded = self.store.load()

        self.assertEqual(3, receipt.persisted_revision)
        self.assertEqual(2, receipt.prior_persisted_revision)
        self.assertEqual(3, reloaded.revision)
        self.assertIsNotNone(reloaded.node("evidence-2"))

    def test_store_apply_commits_governed_mutations_under_one_durable_boundary(self):
        first_mutation, first_persist = self.store.apply(mutation_one())
        second_mutation, second_persist = self.store.apply(mutation_two())
        loaded = self.store.load()

        self.assertEqual(1, first_mutation.resulting_revision)
        self.assertEqual(1, first_persist.persisted_revision)
        self.assertEqual(2, second_mutation.resulting_revision)
        self.assertEqual(2, second_persist.persisted_revision)
        self.assertEqual(2, loaded.revision)
        self.assertEqual(
            ["EXECUTE_TRANCHE"],
            [
                action.to_dict()["kind"]
                for action in GraphScheduler(loaded).next_actions(
                    PROJECT, run_id="run-persist"
                )
            ],
        )

    def test_candidate_is_replay_validated_before_first_write(self):
        graph = build_graph()
        original = graph._mutation_receipts[0]
        graph._mutation_receipts[0] = MutationReceipt(
            mutation_id=original.mutation_id,
            idempotency_key=original.idempotency_key,
            prior_revision=original.prior_revision,
            resulting_revision=original.resulting_revision,
            status=original.status,
            mutation_digest="0" * 64,
            replayed=original.replayed,
        )

        with self.assertRaisesRegex(GraphPersistenceIntegrityError, "receipts"):
            self.store.save(graph, expected_stored_revision=None)

        self.assertFalse(self.path.exists())

    def test_second_process_cannot_enter_writer_boundary_concurrently(self):
        code = (
            "import sys,time;"
            "from gacm.graph import JsonGovernedGraphStore;"
            "s=JsonGovernedGraphStore(sys.argv[1]);"
            "s.path.parent.mkdir(parents=True,exist_ok=True);"
            "c=s._exclusive_writer();c.__enter__();"
            "print('LOCKED',flush=True);time.sleep(5);c.__exit__(None,None,None)"
        )
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        child = subprocess.Popen(
            [sys.executable, "-B", "-c", code, str(self.path)],
            cwd=str(ROOT),
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            self.assertEqual("LOCKED", child.stdout.readline().strip())
            with self.assertRaises(GraphPersistenceLocked):
                self.store.save(build_graph(), expected_stored_revision=None)
        finally:
            child.terminate()
            child.communicate(timeout=5)

    def test_durable_apply_preserves_idempotent_replay_after_restart(self):
        first, first_persist = self.store.apply(mutation_one())
        replay, replay_persist = self.store.apply(mutation_one())
        loaded = self.store.load()

        self.assertFalse(first.replayed)
        self.assertEqual(1, first_persist.persisted_revision)
        self.assertTrue(replay.replayed)
        self.assertEqual(1, replay_persist.prior_persisted_revision)
        self.assertEqual(1, replay_persist.persisted_revision)
        self.assertEqual(1, loaded.revision)
        self.assertEqual(1, len(loaded.mutations))

    def test_stale_writer_cannot_overwrite_newer_durable_graph(self):
        original = self.save_graph()
        newer = self.store.load()
        newer.apply(
            GraphMutation(
                mutation_id="persist-m3",
                project_id=PROJECT,
                expected_revision=2,
                actor_role=ProducerRole.ORCHESTRATION,
                idempotency_key="persist-key-3",
                nodes=(
                    GraphNode(
                        object_id="newer",
                        project_id=PROJECT,
                        object_type=NodeType.EVIDENCE,
                        epistemic_state=EpistemicState.OBSERVED,
                        status="RECORDED",
                        source="test",
                        provenance=("newer",),
                        producer_role=ProducerRole.ORCHESTRATION,
                        created_at="2026-10-03T23:03:00Z",
                    ),
                ),
                timestamp="2026-10-03T23:03:00Z",
            )
        )
        self.store.save(newer, expected_stored_revision=2)

        original.apply(
            GraphMutation(
                mutation_id="persist-divergent",
                project_id=PROJECT,
                expected_revision=2,
                actor_role=ProducerRole.ORCHESTRATION,
                idempotency_key="persist-divergent",
                nodes=(
                    GraphNode(
                        object_id="stale",
                        project_id=PROJECT,
                        object_type=NodeType.EVIDENCE,
                        epistemic_state=EpistemicState.OBSERVED,
                        status="RECORDED",
                        source="test",
                        provenance=("stale",),
                        producer_role=ProducerRole.ORCHESTRATION,
                        created_at="2026-10-03T23:03:00Z",
                    ),
                ),
                timestamp="2026-10-03T23:03:00Z",
            )
        )
        with self.assertRaises(StalePersistedGraphRevision):
            self.store.save(original, expected_stored_revision=2)

        self.assertEqual(3, self.store.load().revision)
        self.assertIsNotNone(self.store.load().node("newer"))
        self.assertIsNone(self.store.load().node("stale"))

    def test_divergent_history_cannot_replace_same_revision(self):
        self.save_graph()
        divergent = GovernedGraph()
        divergent.apply(
            GraphMutation(
                mutation_id="other-m1",
                project_id=PROJECT,
                expected_revision=0,
                actor_role=ProducerRole.ORCHESTRATION,
                idempotency_key="other-1",
                nodes=(tranche_node(),),
                timestamp="2026-10-03T23:00:00Z",
            )
        )
        divergent.apply(
            GraphMutation(
                mutation_id="other-m2",
                project_id=PROJECT,
                expected_revision=1,
                actor_role=ProducerRole.ORCHESTRATION,
                idempotency_key="other-2",
                nodes=(risk_node(),),
                timestamp="2026-10-03T23:01:00Z",
            )
        )

        with self.assertRaises(StalePersistedGraphRevision):
            self.store.save(divergent, expected_stored_revision=2)

    def test_expected_revision_requires_existing_durable_graph(self):
        with self.assertRaises(StalePersistedGraphRevision):
            self.store.save(build_graph(), expected_stored_revision=0)

    def test_payload_digest_tamper_fails_closed(self):
        self.save_graph()
        record = self.read_record()
        record["graph"]["nodes"][0]["status"] = "TAMPERED"
        self.write_record(record)

        with self.assertRaisesRegex(GraphPersistenceIntegrityError, "digest"):
            self.store.load()

    def test_recomputed_digest_cannot_hide_projection_tamper(self):
        self.save_graph()
        record = self.read_record()
        record["graph"]["nodes"][0]["status"] = "TAMPERED"
        recompute_record_digest(record)
        self.write_record(record)

        with self.assertRaisesRegex(GraphPersistenceIntegrityError, "projection"):
            self.store.load()

    def test_reordered_history_fails_even_with_recomputed_digest(self):
        self.save_graph()
        record = self.read_record()
        record["graph"]["mutation_history"].reverse()
        record["graph"]["mutation_receipts"].reverse()
        recompute_record_digest(record)
        self.write_record(record)

        with self.assertRaisesRegex(GraphPersistenceIntegrityError, "revision sequence"):
            self.store.load()

    def test_receipt_tamper_fails_even_with_recomputed_digest(self):
        self.save_graph()
        record = self.read_record()
        record["graph"]["mutation_receipts"][0]["mutation_digest"] = "0" * 64
        recompute_record_digest(record)
        self.write_record(record)

        with self.assertRaisesRegex(GraphPersistenceIntegrityError, "receipts"):
            self.store.load()

    def test_malformed_or_unsupported_record_fails_closed(self):
        self.path.write_text("{broken", encoding="utf-8")
        with self.assertRaises(GraphPersistenceIntegrityError):
            self.store.load()

        self.save_graph_after_removing_broken_file()
        record = self.read_record()
        record["schema_version"] = "999.0.0"
        recompute_record_digest(record)
        self.write_record(record)
        with self.assertRaisesRegex(GraphPersistenceIntegrityError, "schema"):
            self.store.load()

    def save_graph_after_removing_broken_file(self):
        if self.path.exists():
            self.path.unlink()
        return self.save_graph()

    def test_inspect_reports_non_authoritative_storage_metadata(self):
        self.save_graph()
        info = self.store.inspect()
        self.assertEqual(2, info["revision"])
        self.assertEqual(2, info["mutation_count"])
        self.assertEqual(2, info["node_count"])
        self.assertEqual(1, info["edge_count"])
        self.assertTrue(info["payload_digest"])


if __name__ == "__main__":
    unittest.main()
