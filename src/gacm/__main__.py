from __future__ import annotations

import argparse
import json
from pathlib import Path

from .gate.core import postcheck, preflight, tranche_id_for_range


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
    args = parser.parse_args()
    root = str(Path.cwd())
    tranche_id = args.tranche or tranche_id_for_range(root, args.base, args.head)
    spec = json.loads(Path(root, "tranches", f"{tranche_id}.json").read_text(encoding="utf-8"))
    verdict = preflight(root, spec) if args.pre else postcheck(root, args.base, args.head, spec)
    payload = json.dumps(verdict.as_dict(), sort_keys=True)
    print(payload)
    if args.out: Path(args.out).write_text(payload + "\n", encoding="utf-8")
    return 0 if verdict.status in {"PASS", "NOT_A_TRANCHE"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
