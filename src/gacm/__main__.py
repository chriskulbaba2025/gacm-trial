from __future__ import annotations

import argparse
import json
from pathlib import Path

from .gate.core import postcheck, preflight, tranche_id_for_range
from .metrics.guard import compare
from .metrics.report import load_fixture, render_report
from .metrics.run_record import build_record, write_record


def main() -> int:
    parser = argparse.ArgumentParser(prog="gacm")
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check")
    tranche = check.add_mutually_exclusive_group(required=True)
    tranche.add_argument("--tranche")
    tranche.add_argument("--tranche-from-head", action="store_true")
    check.add_argument("--pre", action="store_true")
    check.add_argument("--base")
    check.add_argument("--head")
    check.add_argument("--out")
    record = sub.add_parser("record")
    record.add_argument("--tranche", required=True)
    record.add_argument("--out")
    record.add_argument("--result", default="PASS")
    report = sub.add_parser("report")
    report.add_argument("--runs", required=True)
    report.add_argument("--fixture-dir", required=True)
    report.add_argument("--out-dir", default=".")
    guard = sub.add_parser("guard")
    guard.add_argument("--base", required=True)
    guard.add_argument("--head", required=True)
    args = parser.parse_args()
    root = str(Path.cwd())
    if args.command == "record":
        destination = Path(args.out or Path(root, "runs", f"{args.tranche}.json"))
        write_record(destination, build_record(args.tranche, {"token_budget": "UNAVAILABLE", "tokens_used": "UNAVAILABLE"}, args.result))
        print(json.dumps({"status": "PASS", "path": str(destination)})); return 0
    if args.command == "report":
        parts = args.runs.split(",") if "," in args.runs else [args.runs.split("-MA-", 1)[0], "MA-" + args.runs.split("-MA-", 1)[1]]
        start, end = parts
        records = [json.loads(Path(root, "runs", f"{item}.json").read_text(encoding="utf-8")) for item in (start, end)]
        markdown, payload = render_report(records, load_fixture(Path(args.fixture_dir)))
        out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)
        (out / "report.md").write_text(markdown, encoding="utf-8"); (out / "report.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"status": "PASS", "out_dir": str(out)})); return 0
    if args.command == "guard":
        verdict = compare(root, args.base, args.head); print(json.dumps(verdict, sort_keys=True)); return 0 if verdict["status"] == "PASS" else 1
    tranche_id = args.tranche or tranche_id_for_range(root, args.base, args.head)
    spec = json.loads(Path(root, "tranches", f"{tranche_id}.json").read_text(encoding="utf-8"))
    verdict = preflight(root, spec) if args.pre else postcheck(root, args.base, args.head, spec)
    payload = json.dumps(verdict.as_dict(), sort_keys=True)
    print(payload)
    if args.out: Path(args.out).write_text(payload + "\n", encoding="utf-8")
    return 0 if verdict.status in {"PASS", "NOT_A_TRANCHE"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
