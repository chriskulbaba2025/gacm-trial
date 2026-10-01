"""Deterministic Phase 13 orchestration over the existing GACM controls.

The harness owns sequencing and durable projection only.  Authority, routing,
execution, verification, repair, promotion, and settle decisions remain owned
by their Phase 3-12 components and are supplied at this boundary as adapters.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol

from gacm.generalization import GeneralizationGate
from gacm.provider_authority import ExternalProviderAuthorityGate


class TopLevelState(StrEnum):
    INITIALIZED = "INITIALIZED"; AUTHORITY_RESOLVED = "AUTHORITY_RESOLVED"
    CONTEXT_RESOLVED = "CONTEXT_RESOLVED"; PLANNED = "PLANNED"; EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"; REPAIR_REQUIRED = "REPAIR_REQUIRED"; REPAIRING = "REPAIRING"
    PROMOTION_READY = "PROMOTION_READY"; PROMOTION_PENDING = "PROMOTION_PENDING"
    SETTLE_REQUIRED = "SETTLE_REQUIRED"; SETTLING = "SETTLING"; ROLLBACK_REQUIRED = "ROLLBACK_REQUIRED"
    BLOCKED = "BLOCKED"; FAILED = "FAILED"; COMPLETED = "COMPLETED"


TERMINAL = {TopLevelState.COMPLETED, TopLevelState.BLOCKED, TopLevelState.FAILED, TopLevelState.ROLLBACK_REQUIRED}


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
    settle_required: bool = True
    generalization_contract: Mapping[str, Any] = field(default_factory=dict)
    external_provider_authority: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class HarnessAdapters:
    authority: Callable[[HarnessConfig], Any]
    discovery: Callable[[HarnessConfig, Any], Any]
    context: Callable[[HarnessConfig, Any, Any], Any]
    plan: Callable[[HarnessConfig, Any, Any], list[Mapping[str, Any]]]
    route: Callable[[Mapping[str, Any]], Any]
    execute: Callable[[Mapping[str, Any], Any, Any], Any]
    verify: Callable[[Mapping[str, Any], Any, Any], Any]
    repair_plan: Callable[[Mapping[str, Any], Any, Any], Any] | None = None
    repair: Callable[[Mapping[str, Any], Any, Any], Any] | None = None
    identity_validate: Callable[[Mapping[str, Any], Any], Any] | None = None
    promotion: Callable[[Mapping[str, Any], Mapping[str, Any]], Any] | None = None
    settle: Callable[[Mapping[str, Any], Mapping[str, Any]], Any] | None = None
    rollback: Callable[[Mapping[str, Any], Mapping[str, Any]], Any] | None = None
    current_authority: Callable[[HarnessConfig], str] | None = None
    human_approval: Callable[[Mapping[str, Any], Mapping[str, Any]], bool] | None = None
    generalization_evidence: Callable[[Mapping[str, Any], Mapping[str, Any]], Mapping[str, Any]] | None = None


class RunStateStore(Protocol):
    def save(self, state: Mapping[str, Any]) -> None: ...
    def load(self, run_id: str) -> Mapping[str, Any] | None: ...


class MemoryRunStateStore:
    def __init__(self): self.states: dict[str, dict[str, Any]] = {}
    def save(self, state): self.states[str(state["run_id"])] = json.loads(json.dumps(state, default=str))
    def load(self, run_id): return self.states.get(run_id)


class JsonRunStateStore:
    def __init__(self, directory: Path): self.directory = Path(directory); self.directory.mkdir(parents=True, exist_ok=True)
    def _path(self, run_id): return self.directory / f"{run_id}.json"
    def save(self, state): self._path(str(state["run_id"])).write_text(json.dumps(state, indent=2, sort_keys=True, default=str), encoding="utf-8")
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
    receipts: dict[str, list[dict[str, Any]]] = field(default_factory=lambda: {"verification": [], "repair": [], "generalization": [], "provider_authority": [], "promotion": [], "settle": [], "rollback": []})
    assurance_preserved: list[str] = field(default_factory=list)
    human_action_required: bool = False
    generalization_contract_digest: str | None = None
    generalization_gate: dict[str, Any] | None = None

    def snapshot(self) -> dict[str, Any]:
        return {"run_id": self.run_id, "config": asdict(self.config), "state": self.state.value,
                "events": self.events, "evidence": self.evidence, "units": self.units,
                "blockers": self.blockers, "receipts": self.receipts,
                "assurance_preserved": self.assurance_preserved, "human_action_required": self.human_action_required,
                "generalization_contract_digest": self.generalization_contract_digest,
                "generalization_gate": self.generalization_gate}

    @classmethod
    def restore(cls, raw: Mapping[str, Any]) -> "PilotState":
        config = HarnessConfig(**raw["config"])
        receipts = dict(raw.get("receipts", {}))
        for key in ("verification", "repair", "generalization", "provider_authority", "promotion", "settle", "rollback"):
            receipts.setdefault(key, [])
        return cls(
            run_id=str(raw["run_id"]),
            config=config,
            state=TopLevelState(raw["state"]),
            events=list(raw.get("events", [])),
            evidence=list(raw.get("evidence", [])),
            units=list(raw.get("units", [])),
            blockers=list(raw.get("blockers", [])),
            receipts=receipts,
            assurance_preserved=list(raw.get("assurance_preserved", [])),
            human_action_required=bool(raw.get("human_action_required", False)),
            generalization_contract_digest=raw.get("generalization_contract_digest"),
            generalization_gate=dict(raw["generalization_gate"]) if isinstance(raw.get("generalization_gate"), Mapping) else None,
        )


class PilotHarness:
    """One retry-safe lifecycle coordinator; it never manufactures a PASS."""
    def __init__(self, adapters: HarnessAdapters, store: RunStateStore | None = None):
        self.adapters, self.store = adapters, store or MemoryRunStateStore()

    def run(self, config: HarnessConfig, work_units: list[Mapping[str, Any]] | None = None, *, run_id: str | None = None, resume: bool = False, human_approval: bool | None = None) -> dict[str, Any]:
        rid = run_id or self._id(config)
        prior = self.store.load(rid) if resume else None
        if resume and prior is None: raise ValueError("durable run state is missing")
        state = PilotState.restore(prior) if prior else PilotState(rid, config)
        if state.config.authoritative_start_sha != config.authoritative_start_sha or state.config.project_id != config.project_id:
            return self._block(state, "RESUME_IDENTITY_MISMATCH")
        if state.state in TERMINAL: return state.snapshot()
        preflight = self._freeze_generalization_contract(state, config)
        if preflight is not None:
            return preflight
        if resume and self.adapters.current_authority and self.adapters.current_authority(config) != config.authoritative_start_sha:
            return self._block(state, "STALE_AUTHORITY_ON_RESUME")
        try:
            if state.state == TopLevelState.INITIALIZED:
                authority = self.adapters.authority(config); self._require(authority, "VERIFIED", "AMBIGUOUS_AUTHORITY"); state.evidence.append(self._ev("authority", authority)); self._transition(state, TopLevelState.AUTHORITY_RESOLVED)
            authority = state.evidence[0]["value"]
            if state.state == TopLevelState.AUTHORITY_RESOLVED:
                discovery = self.adapters.discovery(config, authority); state.evidence.append(self._ev("discovery", discovery)); context = self.adapters.context(config, authority, discovery); self._require(context, "VERIFIED", "UNRESOLVED_OPERATIONAL_IDENTITY"); state.evidence.append(self._ev("context", context)); self._transition(state, TopLevelState.CONTEXT_RESOLVED)
            context = next(x["value"] for x in state.evidence if x["kind"] == "context")
            if state.state == TopLevelState.CONTEXT_RESOLVED:
                planned = self.adapters.plan(config, context, work_units or []); state.units = [dict(x) for x in planned]; self._require(state.units, True, "EMPTY_PLAN"); self._transition(state, TopLevelState.PLANNED)
            if state.state in {TopLevelState.PLANNED, TopLevelState.EXECUTING, TopLevelState.REPAIRING}:
                self._execute_and_verify(state, config, context)
            if state.state == TopLevelState.VERIFYING:
                self._run_generalization_gate(state, config)
                self._transition(state, TopLevelState.PROMOTION_READY)
            if state.state == TopLevelState.PROMOTION_READY:
                if config.human_authority.get("promotion_required", True) and human_approval is not True and not (self.adapters.human_approval and self.adapters.human_approval(state.snapshot(), config.human_authority)):
                    state.human_action_required = True; self._transition(state, TopLevelState.PROMOTION_PENDING); return self._save(state)
                self._promote(state, config)
            if state.state == TopLevelState.PROMOTION_PENDING:
                if human_approval is not True: return self._save(state)
                self._promote(state, config)
            if state.state == TopLevelState.SETTLE_REQUIRED:
                self._settle(state, config)
            if state.state == TopLevelState.SETTLING: self._settle(state, config)
            return self._save(state)
        except _Blocked as error: return self._block(state, str(error))
        except Exception as error: state.blockers.append(str(error)); state.state = TopLevelState.FAILED; return self._save(state)

    def _execute_and_verify(self, state, config, context):
        self._transition(state, TopLevelState.EXECUTING)
        for unit in state.units:
            if unit.get("status") == "PASS": continue
            if unit.get("external_action_required"):
                pre_request = unit.get("external_provider_request", {})
                pre_gate = ExternalProviderAuthorityGate().evaluate(config.external_provider_authority, pre_request)
                unit["external_provider_pre_execution_gate"] = pre_gate.to_dict()
                self.receipt(state, "provider_authority", pre_gate)
                if pre_gate.status != "PASS":
                    raise _Blocked("EXTERNAL_PROVIDER_AUTHORITY_GATE_HOLD:" + ",".join(pre_gate.reasons))
            route = self.adapters.route(unit)
            if not self._route_is_qualified(route): raise _Blocked("MODEL_QUALIFICATION_MISSING")
            if unit.get("external_action_required"):
                runtime_request = dict(unit.get("external_provider_request", {}))
                route_plain = self._plain(route)
                route_field_map = {
                    "provider_id": ("provider_id", "selected_provider"),
                    "account_identity": ("account_identity", "account_id", "project_id", "tenant_id"),
                    "environment": ("environment",),
                    "endpoint_identity": ("endpoint_identity", "endpoint"),
                    "model_api_variant": ("model_api_variant", "selected_model"),
                    "credential_source_id": ("credential_source_id",),
                }
                for target, candidates in route_field_map.items():
                    for source in candidates:
                        if route_plain.get(source) is not None:
                            runtime_request[target] = route_plain[source]
                            break
                runtime_gate = ExternalProviderAuthorityGate().evaluate(config.external_provider_authority, runtime_request)
                unit["external_provider_runtime_gate"] = runtime_gate.to_dict()
                self.receipt(state, "provider_authority", runtime_gate)
                if runtime_gate.status != "PASS":
                    raise _Blocked("EXTERNAL_PROVIDER_RUNTIME_IDENTITY_HOLD:" + ",".join(runtime_gate.reasons))
            execution = self.adapters.execute(unit, route, context)
            if self._get(execution, "execution_status") != "COMPLETED": raise _Blocked("EXECUTION_FAILED_OR_BLOCKED")
            unit.update({"route": self._plain(route), "execution": self._plain(execution), "status": "EXECUTED"})
            if not self.adapters.identity_validate: raise _Blocked("IDENTITY_VALIDATION_ADAPTER_MISSING")
            identity = self.adapters.identity_validate(unit, context)
            unit["identity_validation"] = self._plain(identity)
            if self._get(identity, "result") != "VALID": raise _Blocked("PLACEHOLDER_OR_IDENTITY_VALIDATION_FAILED")
            self._transition(state, TopLevelState.VERIFYING)
            verification = self.adapters.verify(unit, execution, context)
            unit["verification"] = self._plain(verification)
            self.receipt(state, "verification", verification)
            attempts = 0
            while self._get(verification, "status") != "PASS" or self._get(verification, "issuer_role") != "INDEPENDENT_VERIFIER":
                if not self.adapters.repair_plan or not self.adapters.repair:
                    raise _Blocked("MISSING_OR_UNRESOLVED_VERIFICATION")
                if attempts >= 3:
                    raise _Blocked("REPAIR_ATTEMPT_LIMIT_REACHED")
                self._transition(state, TopLevelState.REPAIR_REQUIRED)
                plan = self.adapters.repair_plan(unit, verification, state.snapshot())
                self._require(plan, "PLANNED", "REPAIR_SCOPE_UNRESOLVED")
                self._transition(state, TopLevelState.REPAIRING)
                repaired = self.adapters.repair(unit, plan, context)
                self.receipt(state, "repair", plan)
                attempts += 1
                verification = self.adapters.verify(unit, repaired, context)
                unit[f"verification_after_repair_{attempts}"] = self._plain(verification)
                self.receipt(state, "verification", verification)
            unit["status"] = "PASS"
        self._transition(state, TopLevelState.VERIFYING)

    def _freeze_generalization_contract(self, state, config):
        gate = GeneralizationGate()
        preflight = gate.preflight(config.generalization_contract)
        if preflight.status == "HOLD":
            return self._block(state, "GENERALIZATION_CONTRACT_INVALID:" + ",".join(preflight.reasons))
        digest = preflight.contract_digest
        if state.generalization_contract_digest and state.generalization_contract_digest != digest:
            return self._block(state, "FROZEN_ACCEPTANCE_BOUNDARY_CHANGED")
        state.generalization_contract_digest = digest
        self.store.save(state.snapshot())
        return None

    def _run_generalization_gate(self, state, config):
        if state.generalization_gate and state.generalization_gate.get("status") in GeneralizationGate.accepted_statuses:
            return
        if not self.adapters.generalization_evidence:
            raise _Blocked("GENERALIZATION_EVIDENCE_ADAPTER_MISSING")
        evidence = self.adapters.generalization_evidence(state.snapshot(), config.generalization_contract)
        result = GeneralizationGate().evaluate(config.generalization_contract, evidence)
        state.generalization_gate = result.to_dict()
        self.receipt(state, "generalization", result)
        if result.status not in GeneralizationGate.accepted_statuses:
            raise _Blocked("GENERALIZATION_GATE_HOLD:" + ",".join(result.reasons))

    def _promote(self, state, config):
        if not state.generalization_gate or state.generalization_gate.get("status") not in GeneralizationGate.accepted_statuses:
            raise _Blocked("GENERALIZATION_GATE_REQUIRED_BEFORE_PROMOTION")
        if not self.adapters.promotion: raise _Blocked("PROMOTION_ADAPTER_MISSING")
        if self.adapters.current_authority and self.adapters.current_authority(config) != config.authoritative_start_sha:
            raise _Blocked("AUTHORITY_CHANGED_BEFORE_PROMOTION")
        self._transition(state, TopLevelState.PROMOTION_PENDING)
        receipt = self.adapters.promotion(state.snapshot(), config.human_authority)
        if self._get(receipt, "state") not in ("PROMOTED", "SETTLE_REQUIRED", "STABLE"): raise _Blocked("PROMOTION_BLOCKED")
        self.receipt(state, "promotion", receipt)
        self._transition(state, TopLevelState.SETTLE_REQUIRED if config.settle_required else TopLevelState.COMPLETED)

    def _settle(self, state, config):
        if not self.adapters.settle: raise _Blocked("SETTLE_ADAPTER_MISSING")
        self._transition(state, TopLevelState.SETTLING); receipt = self.adapters.settle(state.snapshot(), config.execution_policy); self.receipt(state, "settle", receipt)
        status = self._get(receipt, "status") or self._get(receipt, "state")
        if status in ("PASS", "SETTLE_PASS", "SETTLED", "STABLE"): state.state = TopLevelState.COMPLETED
        else:
            state.state = TopLevelState.ROLLBACK_REQUIRED
            if self.adapters.rollback: self.receipt(state, "rollback", self.adapters.rollback(state.snapshot(), receipt))

    def receipt(self, state, kind, value): state.receipts.setdefault(kind, []).append(self._plain(value)); state.evidence.append(self._ev(kind, value))
    def _save(self, state): self.store.save(state.snapshot()); return state.snapshot()
    def _block(self, state, reason): state.blockers.append(reason); state.state = TopLevelState.BLOCKED; return self._save(state)
    def _transition(self, state, to): state.events.append({"from": state.state.value, "to": to.value, "actor_role": "ORCHESTRATION"}); state.state = to; self.store.save(state.snapshot())
    @staticmethod
    def _get(value, key): return value.get(key) if isinstance(value, Mapping) else getattr(value, key, None)
    @classmethod
    def _route_is_qualified(cls, value):
        if cls._get(value, "status") in ("BLOCKED", "UNQUALIFIED"): return False
        return bool(cls._get(value, "qualification_identity") and cls._get(value, "selected_model"))
    @classmethod
    def _require(cls, value, expected, reason):
        actual = cls._get(value, "status") if expected != True else bool(value)
        if actual != expected: raise _Blocked(reason)
    @staticmethod
    def _plain(value): return value.to_dict() if hasattr(value, "to_dict") else json.loads(json.dumps(value, default=str))
    @classmethod
    def _ev(cls, kind, value):
        raw = cls._plain(value); return {"kind": kind, "value": raw, "evidence_id": kind + "-" + hashlib.sha256(json.dumps(raw, sort_keys=True).encode()).hexdigest()[:20]}
    @staticmethod
    def _id(config): return "run-" + hashlib.sha256(json.dumps(asdict(config), sort_keys=True, default=str).encode()).hexdigest()[:24]


class _Blocked(RuntimeError): pass
