"""GACM generalization and whole-system acceptance controls."""

from .gate import (
    FIXTURE_TARGET_COLLAPSE,
    GATE_ID,
    SEQUENTIAL_BLOCKER_TUNNELING,
    GeneralizationGate,
    GeneralizationGateResult,
    GeneralizationGateStatus,
)
from .scanner import scan_runtime_fixture_dependencies

__all__ = [
    "FIXTURE_TARGET_COLLAPSE",
    "GATE_ID",
    "SEQUENTIAL_BLOCKER_TUNNELING",
    "GeneralizationGate",
    "GeneralizationGateResult",
    "GeneralizationGateStatus",
    "scan_runtime_fixture_dependencies",
]
