"""GACM governed lifecycle harness with finite qualification architecture."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol

from gacm.qualification import EscapeScanResult, QualificationCoordinator, QualificationBlocked


class TopLevelState(StrEnum):
    INITIALIZED = "INITIALIZED"
    AUTHORITY_RESOLVED = "AUTHORITY_RESOLVED"
    CONTEXT_RESOLVED = "CONTEXT_RESOLVED"
    PLANNED = "PLANNED"
    QUALIFYING = "QUALIFYING"
    PROMOTION_READY = "PROMOTION_READY"
    PROMOTION_PENDING = "PROMOTION_PENDING"
    SETTLE_REQUIRED = "SETTLE_REQUIRED"
    SETTLING = "SETTLING"
    ROLLBACK_REQUIRED = "ROLLBACK_REQUIRED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"


TERMINAL = {
    TopLevelState.COMPLETED,
    TopLevelState.BLOCKED,
    TopLevelState.FAILED,
    TopLevelState.ROLLBACK_REQUIRED,
}


@dataclass(frozen=True)
class HarnessConfig:
    project_id: str
    prd_identity: str
    authoritative_start_sha: str
    branch_or_worktree: str
    gacm_version: str
    execution_policy: Mapping[str, Any]
    human_authority: Mapping[str, Any]
    discovery_config: Mapping[str, Any]
    operational_context_requirements: Mapping[str, Any]
    frozen_spec_digest: str
    normative_requirement_ids: tuple[str, ...]
    escape_scan_budget: int
    settle_required: bool = True


@dataclass(frozen=True)
class HarnessAdapters:
    authority: Callable[[HarnessConfig], Any]
    discovery: Callable[[HarnessConfig, Any], Any]
    context: Callable[[HarnessConfig, Any, Any], Any]
    plan: Callable[[HarnessConfig, Any, Any], list[Mapping[str, Any]]]
    qualification_nodes: Callable[[HarnessConfig, Any, list[Mapping[str, Any]]], list[Mapping[str, Any]]]
    qualification_completeness: Callable[[HarnessConfig, tuple[Any, ...]], Mapping[str, Any]]
    qualification_discover: Callable[[Any, Any], Any]
    qualification_repair_plan: Callable[[str, tuple[str, ...], Mapping[str, Any]], Mapping[str, Any]]
    qualification_repair: Callable[[str, tuple[str, ...], Mapping[str, Any], Any], Any]
    qualification_retest: Callable[[Any, Any], Any]
    qualification_escape_scan: Callable[[Any, int, Mapping[str, Any], Any], Any]
    qualification_final_verify_node: Callable[[Any, Any], Any]
    qualification_full_regression: Callable[[Mapping[str, Any], Any], bool]
    qualification_runtime_checks: Callable[[Mapping[str, Any], Any], bool]
    qualification_independent_final_verify: Callable[[Mapping[str, Any], Any], Mapping[str, Any]]
    promotion: Callable[[Mapping[str, Any], Mapping[str, Any]], Any] | None = None
    settle: Callable[[Mapping[str, Any], Mapping[str, Any]], Any] | None = None
    rollback: Callable[[Mapping[str, Any], Mapping[str, Any]], Any] | None = None
    current_authority: Callable[[HarnessConfig], str] | None = None
    current_qualification_identity: Callable[[HarnessConfig], Mapping[str, Any]] | None = None
    human_approval: Callable[[Mapping[str, Any], Mapping[str, Any]], bool] | None = None


class RunStateStore(Protocol):
    def save(self, state: Mapping[str, Any]) -> None: ...
    def load(self, run_id: str) -> Mapping[str, Any] | None: ...


class MemoryRunStateStore:
    def __init__(self):
        self.states: dict[str, dict[str, Any]] = {}

    def save(self, state):
        self.states[str(state["run_id"])] = json.loads(json.dumps(state, default=str))

    def load(self, run_id):
        return self.states.get(run_id)


class JsonRunStateStore:
    def __init__(self, directory: Path):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _path(self, run_id):
        return self.directory / f"{run_id}.json"

    def save(self, state):
        self._path(str(state["run_id"])).write_text(
            json.dumps(state, indent=2, sort_keys=True, default=str),
            encoding="utf-8",
        )

    def load(self, run_id):
        path = self._path(run_id)
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


@dataclass
class PilotState:
    run_id: str
    config: HarnessConfig
    state: TopLevelState = TopLevelState.INITIALIZED
    events: list[dict[str, Any]] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    units: list[dict[str, Any]] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    receipts: dict[str, list[dict[str, Any]]] = field(
        default_factory=lambda: {"promotion": [], "settle": [], "rollback": []}
    )
    qualification: dict[str, Any] = field(default_factory=dict)
    human_action_required: bool = False

    def snapshot(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "config": asdict(self.config),
            "state": self.state.value,
            "events": self.events,
            "evidence": self.evidence,
            "units": self.units,
            "blockers": self.blockers,
            "receipts": self.receipts,
            "qualification": self.qualification,
            "human_action_required": self.human_action_required,
        }

    @classmethod
    def restore(cls, raw: Mapping[str, Any]) -> "PilotState":
        config_raw = dict(raw["config"])
        config_raw["normative_requirement_ids"] = tuple(config_raw["normative_requirement_ids"])
        config = HarnessConfig(**config_raw)
        return cls(
            str(raw["run_id"]),
            config,
            TopLevelState(raw["state"]),
            list(raw.get("events", [])),
            list(raw.get("evidence", [])),
            list(raw.get("units", [])),
            list(raw.get("blockers", [])),
            dict(raw.get("receipts", {})),
            dict(raw.get("qualification", {})),
            bool(raw.get("human_action_required", False)),
        )


class PilotHarness:
    """Retry-safe coordinator. Qualification PASS can only come from the frozen graph path."""

    def __init__(self, adapters: HarnessAdapters, store: RunStateStore | None = None):
        self.adapters = adapters
        self.store = store or MemoryRunStateStore()

    def run(
        self,
        config: HarnessConfig,
        work_units: list[Mapping[str, Any]] | None = None,
        *,
        run_id: str | None = None,
        resume: bool = False,
        human_approval: bool | None = None,
    ) -> dict[str, Any]:
        rid = run_id or self._id(config)
        prior = self.store.load(rid) if resume else None
        if resume and prior is None:
            raise ValueError("durable run state is missing")
        state = PilotState.restore(prior) if prior else PilotState(rid, config)
        if (
            state.config.authoritative_start_sha != config.authoritative_start_sha
            or state.config.project_id != config.project_id
            or state.config.frozen_spec_digest != config.frozen_spec_digest
        ):
            return self._block(state, "RESUME_IDENTITY_MISMATCH")
        if state.state in TERMINAL:
            return state.snapshot()
        if resume:
            mismatch = self._resume_identity_mismatch(state, config)
            if mismatch:
                return self._block(state, mismatch)

        try:
            if state.state == TopLevelState.INITIALIZED:
                authority = self.adapters.authority(config)
                self._require(authority, "VERIFIED", "AMBIGUOUS_AUTHORITY")
                state.evidence.append(self._ev("authority", authority))
                self._transition(state, TopLevelState.AUTHORITY_RESOLVED)

            authority = state.evidence[0]["value"]
            if state.state == TopLevelState.AUTHORITY_RESOLVED:
                discovery = self.adapters.discovery(config, authority)
                state.evidence.append(self._ev("discovery", discovery))
                context = self.adapters.context(config, authority, discovery)
                self._require(context, "VERIFIED", "UNRESOLVED_OPERATIONAL_IDENTITY")
                state.evidence.append(self._ev("context", context))
                self._transition(state, TopLevelState.CONTEXT_RESOLVED)

            context = next(x["value"] for x in state.evidence if x["kind"] == "context")
            if state.state == TopLevelState.CONTEXT_RESOLVED:
                planned = self.adapters.plan(config, context, work_units or [])
                state.units = [dict(x) for x in planned]
                if not state.units:
                    raise _Blocked("EMPTY_PLAN")
                self._transition(state, TopLevelState.PLANNED)

            if state.state in {TopLevelState.PLANNED, TopLevelState.QUALIFYING}:
                self._transition(state, TopLevelState.QUALIFYING)
                coordinator = self._coordinator(config, context, state)
                state.qualification = coordinator.run(state.qualification)
                if not state.qualification.get("pre_promotion", {}).get("ready"):
                    raise _Blocked("QUALIFICATION_PRE_PROMOTION_GATE_BLOCKED")
                self._transition(state, TopLevelState.PROMOTION_READY)

            if state.state == TopLevelState.PROMOTION_READY:
                if (
                    config.human_authority.get("promotion_required", True)
                    and human_approval is not True
                    and not (
                        self.adapters.human_approval
                        and self.adapters.human_approval(state.snapshot(), config.human_authority)
                    )
                ):
                    state.human_action_required = True
                    self._transition(state, TopLevelState.PROMOTION_PENDING)
                    return self._save(state)
                self._promote(state, config)

            if state.state == TopLevelState.PROMOTION_PENDING:
                if human_approval is not True:
                    return self._save(state)
                self._promote(state, config)

            if state.state in {TopLevelState.SETTLE_REQUIRED, TopLevelState.SETTLING}:
                self._settle(state, config, context)
            return self._save(state)
        except (QualificationBlocked, _Blocked) as error:
            return self._block(state, str(error))
        except Exception as error:
            state.blockers.append(str(error))
            state.state = TopLevelState.FAILED
            return self._save(state)

    def _coordinator(self, config: HarnessConfig, context: Any, state: PilotState) -> QualificationCoordinator:
        def nodes():
            return self.adapters.qualification_nodes(config, context, state.units)

        return QualificationCoordinator(
            spec_digest=config.frozen_spec_digest,
            normative_requirement_ids=config.normative_requirement_ids,
            escape_scan_budget=config.escape_scan_budget,
            compile_nodes=nodes,
            completeness_verify=lambda parsed: self.adapters.qualification_completeness(config, parsed),
            discover_node=lambda node: self.adapters.qualification_discover(node, context),
            repair_plan=lambda invariant, ids, qstate: self.adapters.qualification_repair_plan(invariant, ids, qstate),
            repair_execute=lambda invariant, ids, plan: self.adapters.qualification_repair(invariant, ids, plan, context),
            retest_node=lambda node: self.adapters.qualification_retest(node, context),
            escape_scan=lambda graph, budget, qstate: self.adapters.qualification_escape_scan(graph, budget, qstate, context),
            final_verify_node=lambda node: self.adapters.qualification_final_verify_node(node, context),
            full_regression=lambda qstate: self.adapters.qualification_full_regression(qstate, context),
            runtime_checks=lambda qstate: self.adapters.qualification_runtime_checks(qstate, context),
            independent_final_verify=lambda qstate: self.adapters.qualification_independent_final_verify(qstate, context),
        )

    def _resume_identity_mismatch(self, state: PilotState, config: HarnessConfig) -> str | None:
        if self.adapters.current_authority and self.adapters.current_authority(config) != config.authoritative_start_sha:
            return "STALE_AUTHORITY_ON_RESUME"
        graph = state.qualification.get("graph")
        if not graph:
            return None
        if not self.adapters.current_qualification_identity:
            return "QUALIFICATION_IDENTITY_ADAPTER_MISSING"
        current = self.adapters.current_qualification_identity(config)
        if str(current.get("spec_digest", "")) != str(graph.get("spec_digest", "")):
            return "QUALIFICATION_SPEC_DIGEST_CHANGED"
        if str(current.get("graph_digest", "")) != str(graph.get("graph_digest", "")):
            return "QUALIFICATION_GRAPH_DIGEST_CHANGED"
        if int(current.get("denominator", -1)) != int(graph.get("denominator", -2)):
            return "QUALIFICATION_DENOMINATOR_CHANGED"
        return None

    def _promote(self, state: PilotState, config: HarnessConfig) -> None:
        if not state.qualification.get("pre_promotion", {}).get("ready"):
            raise _Blocked("PROMOTION_BEFORE_QUALIFICATION_TERMINATION")
        if not self.adapters.promotion:
            raise _Blocked("PROMOTION_ADAPTER_MISSING")
        if self.adapters.current_authority and self.adapters.current_authority(config) != config.authoritative_start_sha:
            raise _Blocked("AUTHORITY_CHANGED_BEFORE_PROMOTION")
        self._transition(state, TopLevelState.PROMOTION_PENDING)
        receipt = self.adapters.promotion(state.snapshot(), config.human_authority)
        if self._get(receipt, "state") not in ("PROMOTED", "SETTLE_REQUIRED", "STABLE"):
            raise _Blocked("PROMOTION_BLOCKED")
        self.receipt(state, "promotion", receipt)
        self._transition(
            state,
            TopLevelState.SETTLE_REQUIRED if config.settle_required else TopLevelState.COMPLETED,
        )

    def _settle(self, state: PilotState, config: HarnessConfig, context: Any) -> None:
        if not state.qualification.get("pre_promotion", {}).get("ready"):
            raise _Blocked("SETTLE_BEFORE_QUALIFICATION_TERMINATION")
        if not self.adapters.settle:
            raise _Blocked("SETTLE_ADAPTER_MISSING")
        self._transition(state, TopLevelState.SETTLING)
        receipt = self.adapters.settle(state.snapshot(), config.execution_policy)
        self.receipt(state, "settle", receipt)
        status = self._get(receipt, "status") or self._get(receipt, "state")
        settle_ok = status in ("PASS", "SETTLE_PASS", "SETTLED", "STABLE")
        coordinator = self._coordinator(config, context, state)
        state.qualification = coordinator.finalize_after_settle(
            state.qualification,
            settle_succeeded=settle_ok,
        )
        if settle_ok and state.qualification.get("termination", {}).get("complete"):
            state.state = TopLevelState.COMPLETED
        else:
            state.state = TopLevelState.ROLLBACK_REQUIRED
            if self.adapters.rollback:
                self.receipt(state, "rollback", self.adapters.rollback(state.snapshot(), receipt))

    def receipt(self, state: PilotState, kind: str, value: Any) -> None:
        state.receipts.setdefault(kind, []).append(self._plain(value))
        state.evidence.append(self._ev(kind, value))

    def _save(self, state: PilotState) -> dict[str, Any]:
        self.store.save(state.snapshot())
        return state.snapshot()

    def _block(self, state: PilotState, reason: str) -> dict[str, Any]:
        state.blockers.append(reason)
        state.state = TopLevelState.BLOCKED
        return self._save(state)

    def _transition(self, state: PilotState, to: TopLevelState) -> None:
        if state.state != to:
            state.events.append({"from": state.state.value, "to": to.value, "actor_role": "ORCHESTRATION"})
            state.state = to
            self.store.save(state.snapshot())

    @staticmethod
    def _get(value, key):
        return value.get(key) if isinstance(value, Mapping) else getattr(value, key, None)

    @classmethod
    def _require(cls, value, expected, reason):
        actual = cls._get(value, "status")
        if actual != expected:
            raise _Blocked(reason)

    @staticmethod
    def _plain(value):
        return value.to_dict() if hasattr(value, "to_dict") else json.loads(json.dumps(value, default=str))

    @classmethod
    def _ev(cls, kind, value):
        raw = cls._plain(value)
        return {
            "kind": kind,
            "value": raw,
            "evidence_id": kind + "-" + hashlib.sha256(json.dumps(raw, sort_keys=True).encode()).hexdigest()[:20],
        }

    @staticmethod
    def _id(config):
        return "run-" + hashlib.sha256(
            json.dumps(asdict(config), sort_keys=True, default=str).encode()
        ).hexdigest()[:24]


class _Blocked(RuntimeError):
    pass
