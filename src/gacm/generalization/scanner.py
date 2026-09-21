"""Static fixture-dependency scan for runtime sources."""
from __future__ import annotations

import hashlib
import re
from typing import Any, Iterable, Mapping

_TEST_FIXTURE_PATTERNS = (
    re.compile(r"(?:^|[/'\".])tests?[/'\".]fixtures?(?:[/'\".]|$)", re.IGNORECASE),
    re.compile(r"\b(?:test_only|test-only|fixture_only|fixture-only)_?fallback\b", re.IGNORECASE),
    re.compile(r"\b(?:known_case|reference_case|fixture_id)\s*==\s*['\"][^'\"]+['\"]", re.IGNORECASE),
)


def scan_runtime_fixture_dependencies(runtime_sources: Mapping[str, str], reference_tokens: Iterable[str] = ()) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    tokens = tuple(sorted({str(token) for token in reference_tokens if str(token)}))
    for path, content in sorted(runtime_sources.items()):
        text = str(content)
        for pattern in _TEST_FIXTURE_PATTERNS:
            match = pattern.search(text)
            if match:
                findings.append({"path": str(path), "kind": "PROHIBITED_FIXTURE_PATTERN", "match": match.group(0)[:160]})
        for token in tokens:
            if token in text:
                findings.append({"path": str(path), "kind": "REFERENCE_TOKEN_IN_RUNTIME", "match": token[:160]})
    material = "\n".join(f"{path}\n{runtime_sources[path]}" for path in sorted(runtime_sources)) + "\n" + "\n".join(tokens)
    scanner_id = "fixture-scan-" + hashlib.sha256(material.encode("utf-8")).hexdigest()[:24]
    return {
        "status": "PASS" if not findings else "FAIL",
        "scanner_id": scanner_id,
        "scanned_paths": sorted(map(str, runtime_sources.keys())),
        "findings": findings,
        "reference_tokens_checked": list(tokens),
    }
