from __future__ import annotations

import ast
import subprocess
from pathlib import PurePosixPath


def _files(root: str, revision: str) -> list[str]:
    output = subprocess.check_output(["git", "-C", root, "ls-tree", "-r", "--name-only", revision, "tests"], text=True)
    return [line for line in output.splitlines() if line.endswith(".py")]


def _source(root: str, revision: str, path: str) -> str:
    return subprocess.check_output(["git", "-C", root, "show", f"{revision}:{path}"], text=True)


def inventory(source: str) -> tuple[set[str], int, int]:
    tree = ast.parse(source)
    ids: set[str] = set()
    assertions = 0
    skips = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
            ids.add(node.name)
        if isinstance(node, ast.Assert): assertions += 1
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr.startswith("assert"): assertions += 1
            if node.func.attr == "skipTest": skips += 1
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            skips += sum(1 for decorator in node.decorator_list if isinstance(decorator, ast.Name) and decorator.id.startswith("skip"))
    return ids, assertions, skips


def compare(root: str, base: str, head: str) -> dict[str, object]:
    base_ids: set[str] = set(); head_ids: set[str] = set(); base_assertions = head_assertions = base_skips = head_skips = 0
    for path in set(_files(root, base)) | set(_files(root, head)):
        try: b_ids, b_assert, b_skip = inventory(_source(root, base, path))
        except subprocess.CalledProcessError: b_ids, b_assert, b_skip = set(), 0, 0
        try: h_ids, h_assert, h_skip = inventory(_source(root, head, path))
        except subprocess.CalledProcessError: h_ids, h_assert, h_skip = set(), 0, 0
        base_ids |= {f"{path}:{item}" for item in b_ids}; head_ids |= {f"{path}:{item}" for item in h_ids}; base_assertions += b_assert; head_assertions += h_assert; base_skips += b_skip; head_skips += h_skip
    removed = sorted(base_ids - head_ids)
    assertion_drop = max(0, base_assertions - head_assertions)
    failures = []
    if removed: failures.append("REMOVED_TEST_IDS")
    if assertion_drop: failures.append("ASSERTION_COUNT_DROP")
    if head_skips > base_skips: failures.append("SKIP_COUNT_INCREASE")
    return {"status": "FAIL" if failures else "PASS", "reasons": failures, "removed_test_ids": removed, "base_assertions": base_assertions, "head_assertions": head_assertions, "base_skips": base_skips, "head_skips": head_skips}
