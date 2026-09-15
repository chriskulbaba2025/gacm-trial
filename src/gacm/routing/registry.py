"""Configurable qualification registry for the pilot model classes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import CapabilityClass, ModelQualification


@dataclass(frozen=True)
class ModelRegistry:
    entries: tuple[ModelQualification, ...]

    def __init__(self, entries: Iterable[ModelQualification]):
        values = tuple(entries)
        if len({entry.model_id for entry in values}) != len(values):
            raise ValueError("model IDs must be unique")
        object.__setattr__(self, "entries", values)

    def qualified_for(self, required_class: CapabilityClass, highest_score: int) -> tuple[ModelQualification, ...]:
        return tuple(
            entry
            for entry in self.entries
            if entry.qualified
            and entry.model_class >= required_class
            and entry.max_dimension_score >= highest_score
        )

    def get(self, model_id: str) -> ModelQualification:
        for entry in self.entries:
            if entry.model_id == model_id:
                return entry
        raise KeyError(model_id)


def default_pilot_registry(
    *,
    luna_model: str = "gpt-5.6-luna",
    terra_model: str = "gpt-5.6-terra",
    sol_model: str = "gpt-5.6-sol",
) -> ModelRegistry:
    """Return the pilot registry; provider/model identifiers remain configurable."""

    return ModelRegistry(
        (
            ModelQualification(luna_model, CapabilityClass.MECHANICAL, "openai", "qual-luna-pilot-v1", 1, 1),
            ModelQualification(terra_model, CapabilityClass.PRECISION, "openai", "qual-terra-pilot-v1", 2, 2),
            ModelQualification(sol_model, CapabilityClass.ARCHITECTURE, "openai", "qual-sol-pilot-v1", 4, 3),
        )
    )
