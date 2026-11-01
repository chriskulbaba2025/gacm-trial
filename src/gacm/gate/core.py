from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from ..metrics.autonomy import declared_class_is_safe, risk_class, validate_codeowners


@dataclass(frozen=True)
class Verdict:
    status: str
    reasons: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {"status": self.status, "reasons": list(self.reasons)}


def _git(root: str, *args: str) -> str:
    return subprocess.check_output(["git", "-C", root, *args], text=True, stderr=subprocess.STDOUT).strip()


def _glob(pattern: str) -> re.Pattern[str]:
    out = ""
    i = 0
    while i < len(pattern):
        if pattern[i : i + 3] == "/**/": out += "(?:/.+)?/"; i += 4
        elif pattern[i : i + 2] == "**": out += ".*"; i += 2
        elif pattern[i] == "*": out += "[^/]*"; i += 1
        else: out += re.escape(pattern[i]); i += 1
    return re.compile("^" + out + "$", re.IGNORECASE)


def matches(path: str, patterns: list[str]) -> bool:
    return any(_glob(p).match(path) for p in patterns)


def unsafe_path(path: str) -> bool:
    p = path.replace("\\", "/")
    return p.startswith("/") or bool(re.match(r"^[A-Za-z]:/", p)) or ".." in PurePosixPath(p).parts or "\x00" in p


def changed_paths(root: str, merge_base: str, head: str) -> tuple[list[str], list[tuple[str, str, str]]]:
    lines = _git(root, "diff", "--name-status", "--find-renames", f"{merge_base}..{head}").splitlines()
    paths: list[str] = []
    modes: list[tuple[str, str, str]] = []
    for line in lines:
        fields = line.split("\t")
        if not fields: continue
        status = fields[0]
        names = fields[1:] if status.startswith("R") else fields[1:2]
        paths.extend(names)
    raw_lines = _git(root, "diff", "--raw", "--find-renames", f"{merge_base}..{head}").splitlines()
    for line in raw_lines:
        match = re.match(r":([0-9]+) ([0-9]+) ([0-9a-f]+) ([0-9a-f]+)\s+([A-Z0-9]+)\s+(.+)$", line)
        if match:
            modes.append((match.group(1), match.group(2), match.group(5)))
    return paths, modes


def tranche_id_from_trailers(trailers: list[str]) -> str:
    values = [value.strip() for value in trailers if value.strip()]
    if not values:
        raise ValueError("NOT_A_TRANCHE")
    if len(set(values)) != 1:
        raise ValueError("MIXED_OR_MISMATCHED_TRAILER")
    return values[0]


def tranche_id_for_range(root: str, base: str, head: str) -> str:
    merge_base = _git(root, "merge-base", base, head)
    trailers = _git(root, "log", "--format=%(trailers:key=GACM-Tranche,valueonly)", f"{merge_base}..{head}").splitlines()
    return tranche_id_from_trailers(trailers)


def preflight(root: str, spec: dict[str, object]) -> Verdict:
    reasons: list[str] = []
    if _git(root, "status", "--porcelain"):
        reasons.append("DIRTY_WORKTREE")
    if _git(root, "rev-parse", "HEAD") != spec["start_sha"]:
        reasons.append("START_SHA_MISMATCH")
    if _git(root, "branch", "--show-current") != "gacm/ma-1a":
        reasons.append("BRANCH_MISMATCH")
    return Verdict("PASS" if not reasons else "FAIL", tuple(reasons))


def postcheck(root: str, base: str, head: str, spec: dict[str, object]) -> Verdict:
    reasons: list[str] = []
    merge_base = _git(root, "merge-base", base, head)
    if subprocess.run(["git", "-C", root, "merge-base", "--is-ancestor", spec["start_sha"], head]).returncode:
        reasons.append("STALE_START")
    paths, modes = changed_paths(root, merge_base, head)
    for path in paths:
        normalized = path.replace("\\", "/")
        if unsafe_path(normalized): reasons.append("UNSAFE_PATH:" + normalized)
        if matches(normalized, spec["forbidden_paths"]): reasons.append("FORBIDDEN_PATH:" + normalized)
        if not matches(normalized, spec["allowed_paths"]): reasons.append("PATH_OUTSIDE_ALLOWLIST:" + normalized)
    if any(old in {"120000", "160000"} or new in {"120000", "160000"} for old, new, _ in modes): reasons.append("LINK_OR_SUBMODULE")
    trailers = [value for value in _git(root, "log", "--format=%(trailers:key=GACM-Tranche,valueonly)", f"{merge_base}..{head}").splitlines() if value]
    try:
        trailer_id = tranche_id_from_trailers(trailers)
        if trailer_id != spec["tranche_id"]:
            reasons.append("MIXED_OR_MISMATCHED_TRAILER")
    except ValueError as error:
        reasons.append(str(error))
    try:
        base_spec = json.loads(_git(root, "show", f"{base}:tranches/{spec['tranche_id']}.json"))
        if base_spec != spec: reasons.append("TRANCHE_SPEC_MUTATED")
    except subprocess.CalledProcessError:
        pass
    if spec.get("tranche_id") == "MA-3":
        try:
            risk_map = json.loads((Path(root) / "policy" / "risk_paths.json").read_text(encoding="utf-8"))
            computed = risk_class(paths, risk_map, not_a_tranche=False)
            if not declared_class_is_safe(str(spec.get("declared_risk_class", "high")), computed):
                reasons.append("DECLARED_RISK_LOWER_THAN_COMPUTED")
            owners = (Path(root) / ".github" / "CODEOWNERS").read_text(encoding="utf-8")
            if not validate_codeowners(owners, risk_map):
                reasons.append("CODEOWNERS_RISK_MAP_DRIFT")
        except (OSError, ValueError, json.JSONDecodeError):
            reasons.append("RISK_POLICY_UNAVAILABLE")
    if reasons == ["NOT_A_TRANCHE"]:
        return Verdict("NOT_A_TRANCHE", tuple(reasons))
    return Verdict("PASS" if not reasons else "FAIL", tuple(reasons))
