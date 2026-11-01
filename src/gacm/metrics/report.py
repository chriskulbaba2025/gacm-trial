from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


def load_fixture(directory: Path) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name in ("prs", "checks", "issues", "main_commits"):
        path = directory / f"{name}.json"
        result[name] = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None
    return result


def _unknown() -> str:
    return "UNKNOWN"


def observe_run(record: Mapping[str, Any], fixture: Mapping[str, Any]) -> dict[str, Any]:
    tranche = record["tranche_id"]
    prs = fixture.get("prs")
    pr = next((item for item in prs or [] if item.get("tranche_id") == tranche or item.get("branch") == f"gacm/{tranche.lower()}"), None)
    if pr is None:
        observed = {"pr": _unknown(), "head_shas_pushed": _unknown(), "first_push_green": _unknown(), "pushes_to_green": _unknown(), "time_to_merge": _unknown(), "changes_requested": _unknown(), "owner_interventions": _unknown(), "escaped_defects": _unknown()}
    else:
        heads = pr.get("head_shas")
        checks = fixture.get("checks") or {}
        first = heads[0] if heads else None
        required = pr.get("required_checks", [])
        first_results = [checks.get(f"{first}:{name}") for name in required] if first else []
        first_green = all(value == "success" for value in first_results) if first_results and all(value is not None for value in first_results) else _unknown()
        green_index = next((index + 1 for index, sha in enumerate(heads or ()) if all(checks.get(f"{sha}:{name}") == "success" for name in required)), None)
        observed = {"pr": pr.get("number", _unknown()), "head_shas_pushed": heads or _unknown(), "first_push_green": first_green, "pushes_to_green": green_index or _unknown(), "time_to_merge": pr.get("time_to_merge", _unknown()), "changes_requested": pr.get("changes_requested", _unknown()), "owner_interventions": pr.get("owner_interventions", _unknown()), "escaped_defects": pr.get("escaped_defects", _unknown())}
    discrepancies = []
    for key, value in record.get("self_reported", {}).items():
        if key in observed and observed[key] != "UNKNOWN" and value != observed[key]:
            discrepancies.append({"field": key, "self_reported": value, "observed": observed[key]})
    return {"tranche_id": tranche, "observed": observed, "discrepancies": discrepancies, "result": "DISCREPANCY" if discrepancies else record.get("result", "UNKNOWN")}


def render_report(records: list[Mapping[str, Any]], fixture: Mapping[str, Any]) -> tuple[str, dict[str, Any]]:
    rows = [observe_run(record, fixture) for record in records]
    payload = {"runs": rows, "count": len(rows)}
    lines = ["# GACM measurement report", "", f"Runs: {len(rows)}", ""]
    for row in rows:
        lines.append(f"## {row['tranche_id']} -- {row['result']}")
        lines.append("")
        lines.append("Observed: " + json.dumps(row["observed"], sort_keys=True))
        if row["discrepancies"]: lines.append("Discrepancies: " + json.dumps(row["discrepancies"], sort_keys=True))
        lines.append("")
    return "\n".join(lines), payload
