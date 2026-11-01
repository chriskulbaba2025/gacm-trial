from __future__ import annotations

from collections.abc import Iterable, Mapping

LEVELS = {0, 1, 2}
RANK = {"low": 0, "medium": 1, "high": 2}


def risk_class(paths: Iterable[str], risk_paths: Mapping[str, list[str]], *, not_a_tranche: bool = False) -> str:
    if not_a_tranche:
        return "high"
    result = "low"
    for path in paths:
        path_class = "high"
        for candidate in ("medium", "low"):
            if any(_match(path, pattern) for pattern in risk_paths.get(candidate, [])):
                path_class = candidate
                break
        if RANK[path_class] > RANK[result]:
            result = path_class
    return result


def _match(path: str, pattern: str) -> bool:
    import fnmatch

    return fnmatch.fnmatchcase(path.replace("\\", "/"), pattern.replace("\\", "/"))


def declared_class_is_safe(declared: str, computed: str) -> bool:
    return declared in RANK and computed in RANK and RANK[declared] >= RANK[computed]


def parse_level(value: object) -> int:
    try:
        level = int(str(value))
    except (TypeError, ValueError):
        return 0
    return level if level in LEVELS else 0


def allowed_at_level(computed: str, level: int) -> bool:
    return computed == "low" and level >= 1 or computed == "medium" and level >= 2


def approval_matches(reviews: Iterable[Mapping[str, object]], owner: str, head_sha: str) -> bool:
    return any(
        review.get("user", {}).get("login") == owner
        and review.get("state") == "APPROVED"
        and review.get("commit_id") == head_sha
        for review in reviews
    )


def recommend(level: int, stats: Mapping[str, Mapping[str, object]]) -> str:
    low = stats.get("low", {})
    medium = stats.get("medium", {})
    if int(low.get("trivial_ignored", 0)) > 0:
        pass
    if int(low.get("escapes", 0)) > 0 or int(medium.get("escapes", 0)) > 0 or int(low.get("discrepancies", 0)) > 0 or int(medium.get("discrepancies", 0)) > 0:
        return "DEMOTE to 0"
    if level == 0 and int(low.get("measured_runs", 0)) >= 5 and int(low.get("first_push_green", 0)) * 100 >= int(low.get("measured_runs", 0)) * 80:
        return "PROMOTE to 1"
    if level == 1 and int(low.get("measured_runs", 0)) >= 10 and int(low.get("first_push_green", 0)) * 100 >= int(low.get("measured_runs", 0)) * 90:
        return "PROMOTE to 2"
    return f"HOLD at {level}"


def codeowners_exceptions(codeowners: str) -> set[str]:
    result: set[str] = set()
    for line in codeowners.splitlines()[1:]:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and len(stripped.split()) == 1:
            result.add(stripped)
    return result


def validate_codeowners(codeowners: str, risk_paths: Mapping[str, list[str]]) -> bool:
    lines = [line.strip() for line in codeowners.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    if not lines or lines[0] != "* @chriskulbaba2025":
        return False
    expected = set(risk_paths.get("low", [])) | set(risk_paths.get("medium", []))
    actual = set()
    for line in lines[1:]:
        fields = line.split()
        if len(fields) == 1:
            actual.add(fields[0])
    return actual == expected
