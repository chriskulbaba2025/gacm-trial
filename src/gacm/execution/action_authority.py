"""Per-action execution authority and inference-state enforcement for GACM."""
from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatchcase
from hashlib import sha256
import json
from typing import Any, Mapping

EXECUTION_STATES = ("DESIGN", "FROZEN", "EXECUTION", "VERIFICATION", "BLOCKED")
RECIPE_SCHEMA = "GACM_EXECUTION_RECIPE_V1"


class ActionAuthorityError(ValueError):
    pass


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def recipe_digest(recipe: Mapping[str, Any]) -> str:
    return sha256(canonical(dict(recipe)).encode("utf-8")).hexdigest()


def validate_recipe(recipe: Mapping[str, Any], work_unit_id: str) -> dict[str, Any]:
    if not isinstance(recipe, Mapping):
        raise ActionAuthorityError("execution recipe is missing")
    required = {
        "schema", "recipe_id", "version", "state", "work_unit_id",
        "mutation_policy", "steps",
    }
    if set(recipe) != required:
        raise ActionAuthorityError("execution recipe fields are invalid")
    if recipe["schema"] != RECIPE_SCHEMA:
        raise ActionAuthorityError("execution recipe schema is unsupported")
    if recipe["state"] != "FROZEN":
        raise ActionAuthorityError("execution recipe is not FROZEN")
    if recipe["work_unit_id"] != work_unit_id:
        raise ActionAuthorityError("execution recipe work unit identity mismatch")
    if recipe["mutation_policy"] != "GOVERNED_REFREEZE_REQUIRED":
        raise ActionAuthorityError("execution recipe mutation policy is invalid")
    if not isinstance(recipe["recipe_id"], str) or not recipe["recipe_id"].strip():
        raise ActionAuthorityError("execution recipe id is required")
    if not isinstance(recipe["version"], str) or not recipe["version"].strip():
        raise ActionAuthorityError("execution recipe version is required")
    steps = recipe["steps"]
    if not isinstance(steps, list) or not steps:
        raise ActionAuthorityError("execution recipe requires steps")
    seen_steps: set[str] = set()
    expected_sequence = 1
    for step in steps:
        if not isinstance(step, Mapping):
            raise ActionAuthorityError("execution recipe step is invalid")
        required_step = {
            "step_id", "sequence", "allowed_actions", "bounded_judgment_slots",
            "acceptable_prior_states", "expected_result_states",
            "evidence_requirements", "stop_conditions",
        }
        if set(step) != required_step:
            raise ActionAuthorityError("execution recipe step fields are invalid")
        step_id = step["step_id"]
        if not isinstance(step_id, str) or not step_id or step_id in seen_steps:
            raise ActionAuthorityError("execution recipe step id is invalid")
        seen_steps.add(step_id)
        if step["sequence"] != expected_sequence:
            raise ActionAuthorityError("execution recipe step sequence is invalid")
        expected_sequence += 1
        if not isinstance(step["allowed_actions"], list) or not step["allowed_actions"]:
            raise ActionAuthorityError("execution recipe step requires allowed actions")
        if not isinstance(step["acceptable_prior_states"], list) or not step["acceptable_prior_states"]:
            raise ActionAuthorityError("execution recipe step requires prior states")
        if not isinstance(step["expected_result_states"], list) or not step["expected_result_states"]:
            raise ActionAuthorityError("execution recipe step requires result states")
        if not isinstance(step["evidence_requirements"], list) or not step["evidence_requirements"]:
            raise ActionAuthorityError("execution recipe step requires evidence")
        if not isinstance(step["stop_conditions"], list) or not step["stop_conditions"]:
            raise ActionAuthorityError("execution recipe step requires STOP conditions")
        slots = step["bounded_judgment_slots"]
        if not isinstance(slots, list):
            raise ActionAuthorityError("bounded judgment slots must be explicit")
        slot_ids: set[str] = set()
        for slot in slots:
            if not isinstance(slot, Mapping):
                raise ActionAuthorityError("bounded judgment slot is invalid")
            if set(slot) != {"slot_id", "purpose", "allowed_values", "may_expand_scope"}:
                raise ActionAuthorityError("bounded judgment slot fields are invalid")
            if not isinstance(slot["slot_id"], str) or not slot["slot_id"] or slot["slot_id"] in slot_ids:
                raise ActionAuthorityError("bounded judgment slot id is invalid")
            slot_ids.add(slot["slot_id"])
            if not isinstance(slot["purpose"], str) or not slot["purpose"].strip():
                raise ActionAuthorityError("bounded judgment purpose is required")
            if not isinstance(slot["allowed_values"], list) or not slot["allowed_values"]:
                raise ActionAuthorityError("bounded judgment values are required")
            if slot["may_expand_scope"] is not False:
                raise ActionAuthorityError("bounded judgment may not expand scope")
        for rule in step["allowed_actions"]:
            if not isinstance(rule, Mapping):
                raise ActionAuthorityError("allowed action rule is invalid")
            required_rule = {
                "action_kind", "tools", "target_patterns", "parameter_constraints",
                "judgment_slot_id",
            }
            if set(rule) != required_rule:
                raise ActionAuthorityError("allowed action rule fields are invalid")
            if not isinstance(rule["action_kind"], str) or not rule["action_kind"]:
                raise ActionAuthorityError("allowed action kind is required")
            if not isinstance(rule["tools"], list) or not rule["tools"]:
                raise ActionAuthorityError("allowed action tools are required")
            if not isinstance(rule["target_patterns"], list) or not rule["target_patterns"]:
                raise ActionAuthorityError("allowed action targets are required")
            if not isinstance(rule["parameter_constraints"], Mapping):
                raise ActionAuthorityError("parameter constraints are required")
            slot_id = rule["judgment_slot_id"]
            if slot_id is not None and slot_id not in slot_ids:
                raise ActionAuthorityError("action references unknown judgment slot")
    return json.loads(canonical(dict(recipe)))


@dataclass(frozen=True)
class ProposedAction:
    action_id: str
    step_id: str
    action_kind: str
    tool: str
    target: str
    parameters: Mapping[str, Any] = field(default_factory=dict)
    judgment_slot_id: str | None = None
    judgment_value: str | None = None


@dataclass(frozen=True)
class ActionDecision:
    result: str
    action_id: str
    step_id: str
    recipe_digest: str
    authority_state: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "result": self.result,
            "action_id": self.action_id,
            "step_id": self.step_id,
            "recipe_digest": self.recipe_digest,
            "authority_state": self.authority_state,
            "reason": self.reason,
        }


class ActionAuthorizationGate:
    """Stateful per-action gate for one frozen execution recipe."""

    def __init__(self, recipe: Mapping[str, Any], work_unit_id: str):
        validated = validate_recipe(recipe, work_unit_id)
        self._recipe_json = canonical(validated)
        self.recipe_digest = sha256(self._recipe_json.encode("utf-8")).hexdigest()
        self.state = "EXECUTION"
        self._step_index = 0
        self._allowed_action_ids: set[str] = set()
        self._decisions: list[dict[str, Any]] = []
        self._transitions: list[dict[str, Any]] = []

    def _recipe(self) -> dict[str, Any]:
        return json.loads(self._recipe_json)

    @property
    def current_step(self) -> Mapping[str, Any]:
        return self._recipe()["steps"][self._step_index]

    def authorize(self, action: ProposedAction, observed_state: str) -> ActionDecision:
        if self.state != "EXECUTION":
            return self._deny(action, "execution authority is not in EXECUTION")
        if observed_state not in EXECUTION_STATES:
            return self._deny(action, "observed execution state is invalid")
        step = self.current_step
        if action.step_id != step["step_id"]:
            return self._deny(action, "proposed action is outside the current recipe step")
        if observed_state not in step["acceptable_prior_states"]:
            return self._deny(action, "observed state is not authorized for the current recipe step")
        if action.action_id in self._allowed_action_ids:
            return self._deny(action, "action id has already been authorized")

        matching_rule = None
        for rule in step["allowed_actions"]:
            if action.action_kind != rule["action_kind"] or action.tool not in rule["tools"]:
                continue
            if not any(fnmatchcase(action.target, pattern) for pattern in rule["target_patterns"]):
                continue
            matching_rule = rule
            break
        if matching_rule is None:
            return self._deny(action, "proposed action kind/tool/target is not authorized")

        constraints = matching_rule["parameter_constraints"]
        allowed_keys = set(constraints.get("allowed_keys", []))
        required_keys = set(constraints.get("required_keys", []))
        if set(action.parameters) - allowed_keys:
            return self._deny(action, "proposed action contains unauthorized parameters")
        if required_keys - set(action.parameters):
            return self._deny(action, "proposed action is missing required parameters")
        for key, expected in constraints.get("exact", {}).items():
            if action.parameters.get(key) != expected:
                return self._deny(action, f"parameter {key} does not match frozen authority")
        for key, values in constraints.get("allowed_values", {}).items():
            if action.parameters.get(key) not in values:
                return self._deny(action, f"parameter {key} is outside bounded authority")
        for key, prefixes in constraints.get("string_prefixes", {}).items():
            value = action.parameters.get(key)
            if not isinstance(value, str) or not any(value.startswith(prefix) for prefix in prefixes):
                return self._deny(action, f"parameter {key} does not match authorized prefix")

        expected_slot = matching_rule["judgment_slot_id"]
        if expected_slot is None:
            if action.judgment_slot_id is not None or action.judgment_value is not None:
                return self._deny(action, "unbounded judgment is not authorized for this action")
        else:
            if action.judgment_slot_id != expected_slot:
                return self._deny(action, "bounded judgment slot identity mismatch")
            slot = next(item for item in step["bounded_judgment_slots"] if item["slot_id"] == expected_slot)
            if action.judgment_value not in slot["allowed_values"]:
                return self._deny(action, "bounded judgment value is outside authorized choices")

        self._allowed_action_ids.add(action.action_id)
        decision = ActionDecision(
            result="ALLOW",
            action_id=action.action_id,
            step_id=action.step_id,
            recipe_digest=self.recipe_digest,
            authority_state=self.state,
            reason="proposed action matches frozen execution authority",
        )
        self._decisions.append(decision.to_dict())
        return decision

    def record_result(
        self,
        action_id: str,
        result_state: str,
        evidence_refs: tuple[str, ...],
    ) -> None:
        if self.state != "EXECUTION":
            raise ActionAuthorityError("execution authority is not active")
        if action_id not in self._allowed_action_ids:
            self.state = "BLOCKED"
            raise ActionAuthorityError("result reported for unauthorized action")
        step = self.current_step
        if result_state not in step["expected_result_states"]:
            self.state = "BLOCKED"
            raise ActionAuthorityError("result state is outside the frozen transition contract")
        if not evidence_refs:
            self.state = "BLOCKED"
            raise ActionAuthorityError("authorized action result lacks evidence")
        self._allowed_action_ids.remove(action_id)
        prior_state = self.state
        prior_step = step["step_id"]
        if self._step_index == len(self._recipe()["steps"]) - 1:
            self.state = "VERIFICATION"
        else:
            self._step_index += 1
        self._transitions.append({
            "action_id": action_id,
            "step_id": prior_step,
            "result_state": result_state,
            "evidence_refs": list(evidence_refs),
            "authority_state_before": prior_state,
            "authority_state_after": self.state,
            "next_step_id": None if self.state == "VERIFICATION" else self.current_step["step_id"],
        })

    def complete(self) -> bool:
        return self.state == "VERIFICATION" and not self._allowed_action_ids

    def evidence(self) -> dict[str, Any]:
        return {
            "kind": "ACTION_AUTHORIZATION_RECEIPT",
            "recipe_digest": self.recipe_digest,
            "final_authority_state": self.state,
            "decisions": list(self._decisions),
            "transitions": list(self._transitions),
            "complete": self.complete(),
        }

    def _deny(self, action: ProposedAction, reason: str) -> ActionDecision:
        self.state = "BLOCKED"
        decision = ActionDecision(
            result="DENY",
            action_id=action.action_id,
            step_id=action.step_id,
            recipe_digest=self.recipe_digest,
            authority_state=self.state,
            reason=reason,
        )
        self._decisions.append(decision.to_dict())
        return decision
