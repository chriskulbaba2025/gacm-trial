"""Bounded TypeSafe Jev classification boundary for GACM.

Jev is advisory classification only. It cannot create graph authority, choose
workflow progression, select an execution model, or issue PASS.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from typing import Any, Callable, Mapping
from urllib import request as urllib_request

from gacm.graph.models import EpistemicState, GraphNode, NodeType, ProducerRole
from gacm.provider_authority import (
    GATE_ID as EXTERNAL_PROVIDER_GATE_ID,
    ExternalProviderGateResult,
)


DEFAULT_JEV_MODEL = "jev-latest"
DEFAULT_JEV_ENDPOINT = "https://api.typesafe.ai/v1/systemone"


class JevClassificationError(RuntimeError):
    """The Jev boundary could not produce a valid governed classification."""


Transport = Callable[[str, Mapping[str, str], Mapping[str, Any]], Mapping[str, Any]]


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class JevClassificationResult:
    requested_model: str
    resolved_model: str
    answers: Mapping[str, Mapping[str, Any]]
    input_tokens: int
    output_tokens: int
    request_digest: str
    result_digest: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "requested_model": self.requested_model,
            "resolved_model": self.resolved_model,
            "answers": {key: dict(value) for key, value in sorted(self.answers.items())},
            "usage": {"input_tokens": self.input_tokens, "output_tokens": self.output_tokens},
            "request_digest": self.request_digest,
            "result_digest": self.result_digest,
            "authoritative": False,
        }

    def choice(self, question_name: str) -> tuple[str, float, Mapping[str, float]]:
        answer = self.answers.get(question_name)
        if not isinstance(answer, Mapping) or answer.get("type") != "choice":
            raise JevClassificationError(f"{question_name} is not a Jev choice answer")
        choice = answer.get("choice")
        confidence = answer.get("confidence")
        probabilities = answer.get("probabilities")
        if not isinstance(choice, str) or not choice:
            raise JevClassificationError(f"{question_name} returned no choice")
        if not isinstance(confidence, (int, float)) or not 0 <= float(confidence) <= 1:
            raise JevClassificationError(f"{question_name} returned invalid confidence")
        if not isinstance(probabilities, Mapping):
            raise JevClassificationError(f"{question_name} returned invalid probabilities")
        return choice, float(confidence), {str(key): float(value) for key, value in probabilities.items()}

    def propose_graph_node(
        self,
        *,
        question_name: str,
        taxonomy_titles: Mapping[str, str],
        object_id: str,
        project_id: str,
        object_type: NodeType | str,
        created_at: str,
        source_snapshot_id: str,
        run_id: str | None = None,
        epistemic_state: EpistemicState | str = EpistemicState.INFERRED,
    ) -> GraphNode:
        """Create a non-authoritative graph candidate with a code-owned title."""

        state = EpistemicState(str(epistemic_state))
        if state not in {EpistemicState.INFERRED, EpistemicState.HYPOTHESIS}:
            raise JevClassificationError("Jev graph candidates may only be INFERRED or HYPOTHESIS")
        code, confidence, probabilities = self.choice(question_name)
        title = taxonomy_titles.get(code)
        if not isinstance(title, str) or not title.strip():
            raise JevClassificationError(f"taxonomy has no deterministic title for {code}")
        return GraphNode(
            object_id=object_id,
            project_id=project_id,
            run_id=run_id,
            object_type=object_type,
            epistemic_state=state,
            status="CLASSIFIED",
            source="typesafe:jev",
            source_snapshot_id=source_snapshot_id,
            provenance=(f"jev-request:{self.request_digest}", f"jev-result:{self.result_digest}"),
            producer_role=ProducerRole.ORCHESTRATION,
            verification_state="NOT_VERIFIED",
            confidence=confidence,
            created_at=created_at,
            payload={
                "classification_code": code,
                "title": title,
                "question_name": question_name,
                "probabilities": dict(probabilities),
                "jev_model": self.resolved_model,
                "jev_requested_model": self.requested_model,
                "input_tokens": self.input_tokens,
                "output_tokens": self.output_tokens,
                "authoritative": False,
            },
        )


class JevClient:
    """Minimal typed Jev client with injectable transport for deterministic tests."""

    def __init__(
        self,
        *,
        model: str = DEFAULT_JEV_MODEL,
        endpoint: str = DEFAULT_JEV_ENDPOINT,
        api_key_env: str = "JEV_API_KEY",
        provider_gate_result: ExternalProviderGateResult | None = None,
        transport: Transport | None = None,
        timeout_seconds: int = 20,
    ):
        if not model.strip() or not endpoint.strip() or not api_key_env.strip():
            raise ValueError("Jev model, endpoint, and API-key environment name are required")
        self.model = model
        self.endpoint = endpoint
        self.api_key_env = api_key_env
        self.provider_gate_result = self._normalize_provider_gate(provider_gate_result)
        self.transport = transport
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def _normalize_provider_gate(value: ExternalProviderGateResult | None) -> dict[str, Any]:
        if value is None:
            return {}
        if not isinstance(value, ExternalProviderGateResult):
            raise ValueError("provider_gate_result must be an evaluated ExternalProviderGateResult")
        return value.to_dict()

    def _validate_provider_gate(self) -> None:
        gate = self.provider_gate_result
        if gate.get("gate_id") != EXTERNAL_PROVIDER_GATE_ID:
            raise JevClassificationError("Jev external action lacks the governed provider-authority gate")
        if gate.get("status") != "PASS" or gate.get("authoritative") is not True:
            raise JevClassificationError("Jev external provider authority is not PASS")
        if gate.get("endpoint_identity") != self.endpoint:
            raise JevClassificationError("Jev endpoint differs from the authorized provider identity")
        if gate.get("model_api_variant") != self.model:
            raise JevClassificationError("Jev model alias differs from the authorized provider identity")
        required = (
            "provider_id",
            "account_identity",
            "credential_source_id",
            "credential_provenance",
            "governing_authority_artifact",
            "authorization_scope",
            "identity_digest",
        )
        if any(not gate.get(field) for field in required):
            raise JevClassificationError("Jev provider gate receipt is incomplete")

    def classify(self, *, state: Any, questions: Mapping[str, Mapping[str, Any]]) -> JevClassificationResult:
        self._validate_provider_gate()
        self._validate_questions(questions)
        payload = {"state": state, "model": self.model, "questions": dict(questions)}
        if self.transport is None:
            api_key = os.environ.get(self.api_key_env, "").strip()
            if not api_key:
                raise JevClassificationError(f"{self.api_key_env} is not set")
            response = self._post(payload, api_key)
        else:
            response = self.transport(self.endpoint, {}, payload)
        return self._parse(payload, response)

    def _post(self, payload: Mapping[str, Any], api_key: str) -> Mapping[str, Any]:
        body = _canonical(payload).encode("utf-8")
        req = urllib_request.Request(
            self.endpoint,
            data=body,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib_request.urlopen(req, timeout=self.timeout_seconds) as response:
                data = json.loads(response.read().decode("utf-8"))
        except Exception as error:
            raise JevClassificationError(f"Jev request failed: {error}") from error
        if not isinstance(data, Mapping):
            raise JevClassificationError("Jev response was not an object")
        return data

    @staticmethod
    def _validate_questions(questions: Mapping[str, Mapping[str, Any]]) -> None:
        if not isinstance(questions, Mapping) or not questions:
            raise JevClassificationError("at least one Jev question is required")
        for name, question in questions.items():
            if not isinstance(name, str) or not name.strip() or not isinstance(question, Mapping):
                raise JevClassificationError("Jev question names and definitions must be non-empty")
            question_type = question.get("type")
            if question_type not in {"choice", "noul", "score"}:
                raise JevClassificationError(f"{name} has unsupported Jev question type")
            if question_type in {"choice", "score"} and not question.get("criteria"):
                raise JevClassificationError(f"{name} requires criteria")

    @staticmethod
    def _validate_answer(
        name: str,
        question: Mapping[str, Any],
        answer: Mapping[str, Any],
    ) -> None:
        answer_type = question.get("type")
        if answer_type == "choice":
            criteria = question.get("criteria")
            choice = answer.get("choice")
            confidence = answer.get("confidence")
            probabilities = answer.get("probabilities")
            if not isinstance(criteria, Mapping) or choice not in criteria:
                raise JevClassificationError(f"Jev returned an out-of-taxonomy choice for {name}")
            if not isinstance(confidence, (int, float)) or not 0 <= float(confidence) <= 1:
                raise JevClassificationError(f"Jev returned invalid confidence for {name}")
            if not isinstance(probabilities, Mapping) or set(probabilities) != set(criteria):
                raise JevClassificationError(f"Jev returned an invalid probability set for {name}")
            values = tuple(probabilities.values())
            if any(
                not isinstance(value, (int, float)) or not 0 <= float(value) <= 1
                for value in values
            ):
                raise JevClassificationError(f"Jev returned invalid probabilities for {name}")
            if abs(sum(float(value) for value in values) - 1.0) > 0.02:
                raise JevClassificationError(f"Jev probabilities do not sum to approximately 1 for {name}")
        elif answer_type == "noul":
            value = answer.get("noul")
            if not isinstance(value, (int, float)) or not 0 <= float(value) <= 1:
                raise JevClassificationError(f"Jev returned invalid noul probability for {name}")
        elif answer_type == "score":
            score = answer.get("score")
            confidence = answer.get("confidence")
            probabilities = answer.get("probabilities")
            legend = answer.get("legend")
            if not isinstance(score, (int, float)):
                raise JevClassificationError(f"Jev returned invalid score for {name}")
            if not isinstance(confidence, (int, float)) or not 0 <= float(confidence) <= 1:
                raise JevClassificationError(f"Jev returned invalid score confidence for {name}")
            if not isinstance(probabilities, Mapping) or not probabilities or not isinstance(legend, Mapping):
                raise JevClassificationError(f"Jev returned invalid score distribution for {name}")
            if set(probabilities) != set(legend):
                raise JevClassificationError(f"Jev score legend and probabilities differ for {name}")
            if any(
                not isinstance(value, (int, float)) or not 0 <= float(value) <= 1
                for value in probabilities.values()
            ):
                raise JevClassificationError(f"Jev returned invalid score probabilities for {name}")

    def _parse(self, payload: Mapping[str, Any], response: Mapping[str, Any]) -> JevClassificationResult:
        resolved_model = response.get("model")
        answers = response.get("answers")
        usage = response.get("usage")
        if not isinstance(resolved_model, str) or not resolved_model:
            raise JevClassificationError("Jev response model is missing")
        if not isinstance(answers, Mapping) or not answers:
            raise JevClassificationError("Jev response answers are missing")
        if set(answers) != set(payload["questions"]):
            raise JevClassificationError("Jev response question set differs from request")
        if not isinstance(usage, Mapping):
            raise JevClassificationError("Jev response usage is missing")
        input_tokens = usage.get("input_tokens")
        output_tokens = usage.get("output_tokens")
        if not isinstance(input_tokens, int) or input_tokens < 0 or not isinstance(output_tokens, int) or output_tokens < 0:
            raise JevClassificationError("Jev token usage is invalid")
        for name, answer in answers.items():
            question = payload["questions"][name]
            if not isinstance(answer, Mapping) or answer.get("type") != question.get("type"):
                raise JevClassificationError(f"Jev answer type mismatch for {name}")
            self._validate_answer(name, question, answer)
        return JevClassificationResult(
            requested_model=self.model,
            resolved_model=resolved_model,
            answers={str(key): dict(value) for key, value in answers.items()},
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            request_digest=_digest(payload),
            result_digest=_digest(response),
        )
