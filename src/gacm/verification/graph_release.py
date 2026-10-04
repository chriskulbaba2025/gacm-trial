"""Independent verification of graph-derived release evidence."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Mapping


GRAPH_RELEASE_CONTRACT_SCHEMA = "GACM_GRAPH_RELEASE_CONTRACT_V1"
GRAPH_RELEASE_EVIDENCE_SCHEMA = "GACM_GRAPH_RELEASE_EVIDENCE_V1"
QUALIFYING_RELEASE_STATES = {"EVIDENCED", "ACCEPTED"}
NON_QUALIFYING_RELEASE_STATES = {
    "USER_STATED",
    "OBSERVED",
    "INFERRED",
    "HYPOTHESIS",
    "CONFLICTED",
    "UNKNOWN",
    "SUPERSEDED",
    "POSSIBLE_SHARED_ROOT_CAUSE",
}


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)


def evidence_digest(value: Mapping[str, Any]) -> str:
    return sha256(canonical(dict(value)).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class GraphReleaseCheck:
    status: str
    evidence_digest: str | None
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "evidence_digest": self.evidence_digest,
            "reasons": list(self.reasons),
        }


def _hex(value: Any, length: int) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and all(ch in "0123456789abcdef" for ch in value.casefold())
    )


def _contract_check(contract: Mapping[str, Any]) -> tuple[list[str], Mapping[str, Any] | None]:
    if contract.get("graph_release_required") is not True:
        return [], None
    value = contract.get("graph_release_contract")
    if not isinstance(value, Mapping):
        return ["graph release contract is required"], None
    required = {
        "schema",
        "project_id",
        "candidate_sha",
        "candidate_artifact_identity",
        "environment_id",
        "graph_schema",
        "graph_engine_authority_sha",
        "graph_engine_manifest_sha256",
        "retrieval_materially_used",
        "convergence_materially_used",
    }
    if set(value) != required:
        return ["graph release contract fields are invalid"], None
    reasons: list[str] = []
    if value.get("schema") != GRAPH_RELEASE_CONTRACT_SCHEMA:
        reasons.append("graph release contract schema is unsupported")
    if not isinstance(value.get("project_id"), str) or not value.get("project_id"):
        reasons.append("graph release project identity is required")
    if not _hex(value.get("candidate_sha"), 40):
        reasons.append("graph release candidate SHA is invalid")
    if not isinstance(value.get("candidate_artifact_identity"), str) or not value.get("candidate_artifact_identity"):
        reasons.append("graph release candidate artifact identity is required")
    if not isinstance(value.get("environment_id"), str) or not value.get("environment_id"):
        reasons.append("graph release environment identity is required")
    if not isinstance(value.get("graph_schema"), str) or not value.get("graph_schema"):
        reasons.append("graph release graph schema is required")
    if not _hex(value.get("graph_engine_authority_sha"), 40):
        reasons.append("graph engine authority SHA is invalid")
    if not _hex(value.get("graph_engine_manifest_sha256"), 64):
        reasons.append("graph engine manifest digest is invalid")
    for flag in ("retrieval_materially_used", "convergence_materially_used"):
        if not isinstance(value.get(flag), bool):
            reasons.append(f"{flag} must be explicit")
    return reasons, value


def check_graph_release(
    contract: Mapping[str, Any],
    evidence: Mapping[str, Any] | None,
) -> GraphReleaseCheck:
    contract_reasons, release_contract = _contract_check(contract)
    if contract.get("graph_release_required") is not True:
        if evidence is None:
            return GraphReleaseCheck("NOT_APPLICABLE", None, ())
        return GraphReleaseCheck(
            "FAIL",
            evidence_digest(evidence) if isinstance(evidence, Mapping) else None,
            ("graph release evidence supplied without graph release authority",),
        )
    if contract_reasons:
        return GraphReleaseCheck("FAIL", None, tuple(sorted(set(contract_reasons))))
    if not isinstance(evidence, Mapping):
        return GraphReleaseCheck("UNOBSERVABLE", None, ("graph release evidence is unavailable",))

    digest = evidence_digest(evidence)
    reasons: list[str] = []
    required_top = {
        "schema",
        "project_id",
        "candidate_sha",
        "candidate_artifact_identity",
        "remote_candidate_sha",
        "deployed_artifact_sha",
        "served_runtime_sha",
        "environment_id",
        "build_identity",
        "source_identities",
        "graph",
        "retrieval",
        "convergence",
        "assertions",
    }
    if set(evidence) != required_top:
        return GraphReleaseCheck("FAIL", digest, ("graph release evidence fields are invalid",))
    if evidence.get("schema") != GRAPH_RELEASE_EVIDENCE_SCHEMA:
        reasons.append("graph release evidence schema is unsupported")
    if evidence.get("project_id") != release_contract["project_id"]:
        reasons.append("graph release project identity mismatch")
    identities = (
        evidence.get("candidate_sha"),
        evidence.get("remote_candidate_sha"),
        evidence.get("deployed_artifact_sha"),
        evidence.get("served_runtime_sha"),
    )
    if any(value != release_contract["candidate_sha"] for value in identities):
        reasons.append("release currentness identity mismatch")
    if evidence.get("candidate_artifact_identity") != release_contract["candidate_artifact_identity"]:
        reasons.append("candidate artifact identity mismatch")
    if evidence.get("environment_id") != release_contract["environment_id"]:
        reasons.append("release environment identity mismatch")
    if not isinstance(evidence.get("build_identity"), str) or not evidence.get("build_identity"):
        reasons.append("release build identity is required")

    sources = evidence.get("source_identities")
    if not isinstance(sources, list) or not sources:
        reasons.append("current authoritative source identities are required")
    else:
        seen_sources: set[str] = set()
        for source in sources:
            if (
                not isinstance(source, Mapping)
                or set(source) != {"source_id", "identity_digest"}
                or not isinstance(source.get("source_id"), str)
                or not source.get("source_id")
                or not _hex(source.get("identity_digest"), 64)
                or source.get("source_id") in seen_sources
            ):
                reasons.append("source identity evidence is invalid")
                break
            seen_sources.add(source["source_id"])

    graph = evidence.get("graph")
    if not isinstance(graph, Mapping):
        reasons.append("graph release identity is unavailable")
        graph = {}
    else:
        required_graph = {
            "schema",
            "status",
            "graph_revision",
            "projection_digest",
            "source_event_hash",
            "engine_authority_sha",
            "engine_manifest_sha256",
        }
        if set(graph) != required_graph:
            reasons.append("graph release identity fields are invalid")
        if graph.get("schema") != release_contract["graph_schema"]:
            reasons.append("graph schema identity mismatch")
        if graph.get("status") != "PASS":
            reasons.append("graph runtime status is not PASS")
        if isinstance(graph.get("graph_revision"), bool) or not isinstance(graph.get("graph_revision"), int) or graph.get("graph_revision", 0) < 1:
            reasons.append("graph revision is invalid")
        if not _hex(graph.get("projection_digest"), 64):
            reasons.append("graph projection digest is invalid")
        if not _hex(graph.get("source_event_hash"), 64):
            reasons.append("graph source event identity is invalid")
        if graph.get("engine_authority_sha") != release_contract["graph_engine_authority_sha"]:
            reasons.append("graph engine authority mismatch")
        if graph.get("engine_manifest_sha256") != release_contract["graph_engine_manifest_sha256"]:
            reasons.append("graph engine manifest identity mismatch")

    graph_revision = graph.get("graph_revision")
    projection_digest = graph.get("projection_digest")
    source_event_hash = graph.get("source_event_hash")

    retrieval = evidence.get("retrieval")
    if release_contract["retrieval_materially_used"]:
        if not isinstance(retrieval, Mapping):
            reasons.append("material retrieval evidence is unavailable")
        else:
            required_retrieval = {
                "materially_used",
                "status",
                "mechanism",
                "index_identity",
                "receipt_digest",
                "graph_revision",
                "projection_digest",
                "corpus_snapshot_digest",
                "query_digest",
                "returned_object_ids",
            }
            if set(retrieval) != required_retrieval:
                reasons.append("retrieval release evidence fields are invalid")
            if retrieval.get("materially_used") is not True or retrieval.get("status") != "AVAILABLE":
                reasons.append("material retrieval evidence is not AVAILABLE")
            if not isinstance(retrieval.get("mechanism"), str) or not retrieval.get("mechanism"):
                reasons.append("retrieval mechanism identity is required")
            if not isinstance(retrieval.get("index_identity"), str) or not retrieval.get("index_identity"):
                reasons.append("retrieval index identity is required")
            for name in ("receipt_digest", "corpus_snapshot_digest", "query_digest"):
                if not _hex(retrieval.get(name), 64):
                    reasons.append(f"retrieval {name} is invalid")
            if retrieval.get("graph_revision") != graph_revision or retrieval.get("projection_digest") != projection_digest:
                reasons.append("material retrieval evidence is stale relative to release graph")
            if not isinstance(retrieval.get("returned_object_ids"), list) or not retrieval.get("returned_object_ids"):
                reasons.append("material retrieval result identity is required")
    else:
        if retrieval is not None:
            if not isinstance(retrieval, Mapping) or retrieval.get("materially_used") is not False:
                reasons.append("non-material retrieval evidence must be explicitly non-material")

    convergence = evidence.get("convergence")
    if release_contract["convergence_materially_used"]:
        if not isinstance(convergence, Mapping):
            reasons.append("material convergence evidence is unavailable")
        else:
            required_convergence = {
                "materially_used",
                "status",
                "detector_identity",
                "result_digest",
                "graph_revision",
                "projection_digest",
                "source_event_hash",
                "candidate_count",
                "epistemic_limit",
                "authority",
                "authoritative_root_cause_established",
                "lexical_similarity_used",
                "vector_similarity_used",
                "model_judgment_used",
            }
            if set(convergence) != required_convergence:
                reasons.append("convergence release evidence fields are invalid")
            if convergence.get("materially_used") is not True or convergence.get("status") != "PASS":
                reasons.append("material convergence evidence is not PASS")
            if not isinstance(convergence.get("detector_identity"), str) or not convergence.get("detector_identity"):
                reasons.append("convergence detector identity is required")
            if not _hex(convergence.get("result_digest"), 64):
                reasons.append("convergence result digest is invalid")
            if (
                convergence.get("graph_revision") != graph_revision
                or convergence.get("projection_digest") != projection_digest
                or convergence.get("source_event_hash") != source_event_hash
            ):
                reasons.append("material convergence evidence is stale relative to release graph")
            if isinstance(convergence.get("candidate_count"), bool) or not isinstance(convergence.get("candidate_count"), int) or convergence.get("candidate_count", -1) < 0:
                reasons.append("convergence candidate count is invalid")
            if convergence.get("epistemic_limit") != "POSSIBLE_SHARED_ROOT_CAUSE":
                reasons.append("convergence epistemic limit is invalid")
            if convergence.get("authority") != "ADVISORY_DIAGNOSTIC_ONLY":
                reasons.append("convergence authority exceeds advisory diagnostic scope")
            if convergence.get("authoritative_root_cause_established") is not False:
                reasons.append("convergence cannot establish authoritative root cause")
            for name in ("lexical_similarity_used", "vector_similarity_used", "model_judgment_used"):
                if convergence.get(name) is not False:
                    reasons.append(f"{name} cannot provide causal release authority")
    else:
        if convergence is not None:
            if not isinstance(convergence, Mapping) or convergence.get("materially_used") is not False:
                reasons.append("non-material convergence evidence must be explicitly non-material")

    assertions = evidence.get("assertions")
    if not isinstance(assertions, list) or not assertions:
        reasons.append("graph-derived release assertions are required")
    else:
        seen_assertions: set[str] = set()
        satisfying_count = 0
        for assertion in assertions:
            required_assertion = {
                "assertion_id",
                "kind",
                "object_ids",
                "evidence_ids",
                "provenance_refs",
                "graph_revision",
                "projection_digest",
                "epistemic_state",
                "verification_state",
                "release_gate_role",
            }
            if not isinstance(assertion, Mapping) or set(assertion) != required_assertion:
                reasons.append("graph-derived release assertion fields are invalid")
                continue
            assertion_id = assertion.get("assertion_id")
            if not isinstance(assertion_id, str) or not assertion_id or assertion_id in seen_assertions:
                reasons.append("graph-derived release assertion identity is invalid")
                continue
            seen_assertions.add(assertion_id)
            if assertion.get("graph_revision") != graph_revision or assertion.get("projection_digest") != projection_digest:
                reasons.append(f"graph-derived assertion {assertion_id} is stale")
            if not isinstance(assertion.get("object_ids"), list) or not assertion.get("object_ids"):
                reasons.append(f"graph-derived assertion {assertion_id} lacks object identity")
            if not isinstance(assertion.get("evidence_ids"), list) or not assertion.get("evidence_ids"):
                reasons.append(f"graph-derived assertion {assertion_id} lacks evidence")
            if not isinstance(assertion.get("provenance_refs"), list) or not assertion.get("provenance_refs"):
                reasons.append(f"graph-derived assertion {assertion_id} lacks provenance")
            role = assertion.get("release_gate_role")
            if role not in {"SATISFIES_RELEASE_GATE", "CONTEXT_ONLY"}:
                reasons.append(f"graph-derived assertion {assertion_id} has invalid release-gate role")
                continue
            epistemic = assertion.get("epistemic_state")
            if role == "SATISFIES_RELEASE_GATE":
                satisfying_count += 1
                if epistemic not in QUALIFYING_RELEASE_STATES:
                    reasons.append(f"graph-derived assertion {assertion_id} epistemic state cannot satisfy release")
                if assertion.get("verification_state") != "VERIFIED":
                    reasons.append(f"graph-derived assertion {assertion_id} is not independently VERIFIED")
            elif epistemic == "POSSIBLE_SHARED_ROOT_CAUSE" and assertion.get("verification_state") == "VERIFIED":
                # Verification may confirm the diagnostic candidate exists, not convert it to causal truth.
                pass
            elif epistemic not in QUALIFYING_RELEASE_STATES | NON_QUALIFYING_RELEASE_STATES:
                reasons.append(f"graph-derived assertion {assertion_id} epistemic state is unsupported")
        if satisfying_count == 0:
            reasons.append("no qualifying graph-derived assertion satisfies the release gate")

    status = "PASS" if not reasons else "FAIL"
    return GraphReleaseCheck(status, digest, tuple(sorted(set(reasons))))
