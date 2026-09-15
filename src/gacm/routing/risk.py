"""Bounded risk-to-capability rules owned by GACM, not by a model."""

from __future__ import annotations

from dataclasses import dataclass

from .models import CapabilityClass, ROUTING_DIMENSIONS, WorkUnit


@dataclass(frozen=True)
class RiskAssessment:
    required_class: CapabilityClass
    highest_risk_dimension: str
    highest_score: int
    dimensions: dict[str, int]


_DIMENSION_ORDER = {name: index for index, name in enumerate(ROUTING_DIMENSIONS)}


def required_class_for_dimension(dimension: str, score: int) -> CapabilityClass:
    """Map a bounded risk score to the minimum capability class."""

    if dimension in {"architectural_impact", "security_sensitivity", "authority_sensitivity"}:
        if score >= 3:
            return CapabilityClass.ARCHITECTURE
        if score >= 2:
            return CapabilityClass.PRECISION
        return CapabilityClass.MECHANICAL
    if score >= 3:
        return CapabilityClass.ARCHITECTURE
    if score >= 2:
        return CapabilityClass.PRECISION
    return CapabilityClass.MECHANICAL


def assess(work_unit: WorkUnit) -> RiskAssessment:
    highest = max(work_unit.dimensions.items(), key=lambda pair: (pair[1], -_DIMENSION_ORDER[pair[0]]))
    required = max(
        (required_class_for_dimension(dimension, score) for dimension, score in work_unit.dimensions.items()),
        default=CapabilityClass.MECHANICAL,
    )
    return RiskAssessment(required, highest[0], highest[1], dict(work_unit.dimensions))
