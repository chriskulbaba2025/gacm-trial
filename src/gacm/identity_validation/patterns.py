"""Extensible deterministic placeholder and prompt-request detection."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


DEFAULT_PLACEHOLDER_PATTERNS = (
    r"<[A-Z][A-Z0-9_ -]*>",
    r"\bYOUR[_ -][A-Z][A-Z0-9_-]*\b",
    r"\b(?:replace|insert)[_-]?(?:this|your|the)[_-]?[A-Z0-9_-]*\b",
    r"\b(?:example|sample|dummy|fake|test)[_-]?(?:account|tenant|region|repo|repository|project|client|environment|branch|service|database|domain)(?:[_-][A-Z0-9.-]+)?\b",
    r"\b(?:account|tenant|project|repo|repository|region|branch|environment)[_-]?(?:id|value)?[_-]?(?:123|000|999|xxxx|changeme)\b",
)

DEFAULT_REPROMPT_PATTERNS = (
    r"\bwhat\s+is\s+your\s+(?:account|tenant|region|repository|repo|project|environment|branch)\s*(?:id)?\b",
    r"\b(?:enter|provide|replace|insert)\s+(?:your|the)\s+(?:account|tenant|region|repository|repo|project|environment|branch)\b",
)


@dataclass(frozen=True)
class PlaceholderMatch:
    pattern: str
    text: str
    start: int
    end: int


class PlaceholderPatterns:
    def __init__(self, patterns: Iterable[str] = DEFAULT_PLACEHOLDER_PATTERNS, reprompt_patterns: Iterable[str] = DEFAULT_REPROMPT_PATTERNS):
        self.patterns = tuple(patterns)
        self.reprompt_patterns = tuple(reprompt_patterns)
        self._compiled = tuple(re.compile(pattern, re.IGNORECASE) for pattern in self.patterns)
        self._reprompt_compiled = tuple(re.compile(pattern, re.IGNORECASE) for pattern in self.reprompt_patterns)

    def find(self, text: str) -> tuple[PlaceholderMatch, ...]:
        matches = []
        for source, compiled in ((self.patterns, self._compiled), (self.reprompt_patterns, self._reprompt_compiled)):
            for pattern, regex in zip(source, compiled):
                for match in regex.finditer(text):
                    matches.append(PlaceholderMatch(pattern, match.group(0), match.start(), match.end()))
        return tuple(sorted(matches, key=lambda item: (item.start, item.end, item.pattern)))
