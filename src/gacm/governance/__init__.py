"""Machine-enforced governance gates for cumulative GACM qualification."""

from .gates import (
    DRIFT_GATE_ID,
    DRIFT_FIELDS,
    WHOLE_MACHINE_GATE_ID,
    DriftCheck,
    GateDecision,
    acceptance_readiness,
    check_frozen_start,
    evaluate_instruction_authority_drift,
    evaluate_whole_machine_integrity,
)

__all__ = [
    "DRIFT_GATE_ID",
    "DRIFT_FIELDS",
    "WHOLE_MACHINE_GATE_ID",
    "DriftCheck",
    "GateDecision",
    "acceptance_readiness",
    "check_frozen_start",
    "evaluate_instruction_authority_drift",
    "evaluate_whole_machine_integrity",
]
