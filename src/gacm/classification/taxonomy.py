"""Initial deterministic GACM classification taxonomy.

Jev selects a fixed code. GACM code owns the title and graph-node mapping.
"""

from __future__ import annotations

from gacm.graph.models import NodeType


GACM_INPUT_KIND_TITLES = {
    "DEFECT": "Defect",
    "EVIDENCE_GAP": "Evidence Gap",
    "REQUIREMENT": "Requirement",
    "CONSTRAINT": "Constraint",
    "DEPENDENCY": "Dependency",
    "RISK": "Risk",
    "UNKNOWN": "Unknown",
}

GACM_INPUT_KIND_NODE_TYPES = {
    "DEFECT": NodeType.DEFECT,
    "EVIDENCE_GAP": NodeType.EVIDENCE_GAP,
    "REQUIREMENT": NodeType.REQUIREMENT,
    "CONSTRAINT": NodeType.CONSTRAINT,
    "DEPENDENCY": NodeType.DEPENDENCY,
    "RISK": NodeType.RISK,
    "UNKNOWN": NodeType.UNKNOWN,
}

GACM_INPUT_KIND_QUESTION = {
    "type": "choice",
    "instructions": (
        "Classify the primary governed object represented by the supplied state. "
        "Choose UNKNOWN when the state does not support a reliable category."
    ),
    "criteria": {
        "DEFECT": "Observed behavior or state is wrong, broken, or violates an expected contract.",
        "EVIDENCE_GAP": "A decision or verification is blocked because required evidence is missing.",
        "REQUIREMENT": "The state expresses a capability, behavior, or outcome the system must provide.",
        "CONSTRAINT": "The state limits what may be changed, selected, executed, or accepted.",
        "DEPENDENCY": "The state primarily describes reliance on another component, artifact, service, or prerequisite.",
        "RISK": "The state primarily describes a possible harmful outcome or exposure that has not necessarily occurred.",
        "UNKNOWN": "The supplied state is too ambiguous to classify into another governed category.",
    },
}


def deterministic_title(classification_code: str) -> str:
    try:
        return GACM_INPUT_KIND_TITLES[classification_code]
    except KeyError as error:
        raise ValueError(f"unknown GACM classification code: {classification_code}") from error


def graph_node_type(classification_code: str) -> NodeType:
    try:
        return GACM_INPUT_KIND_NODE_TYPES[classification_code]
    except KeyError as error:
        raise ValueError(f"unknown GACM classification code: {classification_code}") from error
