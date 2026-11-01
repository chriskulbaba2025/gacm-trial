from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


FIELDS = ("token_budget", "tokens_used", "tool_calls", "round_trips", "wall_clock_ms", "repair_attempts", "human_interventions", "reruns_avoided", "evidence_artifacts")


def build_record(tranche_id: str, self_reported: Mapping[str, Any], result: str = "PASS", backfilled: bool = False) -> dict[str, Any]:
    data = dict(self_reported)
    for field in FIELDS:
        data.setdefault(field, "UNAVAILABLE")
    data.setdefault("targeted_tests", [])
    data.setdefault("broad_regression", "UNAVAILABLE")
    data["tokens_used"] = data.get("tokens_used", "UNAVAILABLE")
    return {"tranche_id": tranche_id, "self_reported": data, "result": result, "backfilled": backfilled}


def write_record(path: Path, record: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
