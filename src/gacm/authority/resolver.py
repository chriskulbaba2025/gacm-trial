"""Deterministic Git authority resolution for GACM Pilot v1.

This module reads repository state through Git commands. It does not use model
judgment, chat context, Graphify, or a second authority source to resolve a
conflict.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence
from urllib.parse import urlparse


SHA_RE = re.compile(r"^[0-9a-f]{40}$")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


class GitAuthorityError(RuntimeError):
    """Raised only for internal command failures converted to BLOCKED results."""


@dataclass(frozen=True)
class ResolverConfig:
    repository_path: Path
    intended_branch: str
    remote_name: str = "origin"
    intended_ref: str | None = None
    expected_repository: str | None = None
    authorized_head: str | None = None
    required_authority_files: tuple[str, ...] = (
        "CURRENT_STATE.md",
        "GACM_IMPLEMENTATION_PRD_V1.0.md",
    )
    protected_rollback_sha: str | None = None

    def remote_ref(self) -> str:
        return self.intended_ref or f"refs/heads/{self.intended_branch}"


@dataclass
class ResolutionResult:
    status: str
    repository: str | None = None
    remote_url: str | None = None
    remote_name: str | None = None
    remote_ref: str | None = None
    branch: str | None = None
    local_head: str | None = None
    remote_head: str | None = None
    worktree_clean: bool | None = None
    divergence: str = "UNKNOWN"
    authority_files: list[str] = field(default_factory=list)
    missing_authority_files: list[str] = field(default_factory=list)
    repository_identity_match: bool | None = None
    authorized_head_match: bool | None = None
    local_matches_remote: bool | None = None
    blocking_reasons: list[str] = field(default_factory=list)
    ambiguous_reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "repository": self.repository,
            "remote_url": self.remote_url,
            "remote_name": self.remote_name,
            "remote_ref": self.remote_ref,
            "branch": self.branch,
            "local_head": self.local_head,
            "remote_head": self.remote_head,
            "worktree_clean": self.worktree_clean,
            "divergence": self.divergence,
            "authority_files": self.authority_files,
            "missing_authority_files": self.missing_authority_files,
            "repository_identity_match": self.repository_identity_match,
            "authorized_head_match": self.authorized_head_match,
            "local_matches_remote": self.local_matches_remote,
            "blocking_reasons": self.blocking_reasons,
            "ambiguous_reasons": self.ambiguous_reasons,
        }

    def to_run_state_patch(self, config: ResolverConfig) -> dict[str, Any]:
        """Return fields that can be inserted into a Phase 2 run-state snapshot.

        A protected rollback SHA is required because the Phase 2 schema requires
        a durable rollback identity. The resolver does not invent one.
        """

        if self.status != "VERIFIED":
            raise ValueError("only VERIFIED authority results can populate run state")
        if not self.local_head or not self.remote_url or not self.branch:
            raise ValueError("verified result lacks repository identity fields")
        if not config.protected_rollback_sha or not SHA_RE.fullmatch(config.protected_rollback_sha):
            raise ValueError("protected_rollback_sha is required for run-state projection")

        repository_id = self.repository or ""
        if not ID_RE.fullmatch(repository_id):
            repository_id = "remote-" + hashlib.sha256(repository_id.encode("utf-8")).hexdigest()[:32]
        prd_path = next(
            (Path(item) for item in config.required_authority_files if Path(item).name == "GACM_IMPLEMENTATION_PRD_V1.0.md"),
            None,
        )
        if prd_path is None:
            raise ValueError("required authority files must include GACM_IMPLEMENTATION_PRD_V1.0.md")
        prd_sha = self._git_hash_object(config.repository_path, prd_path)

        return {
            "current_repository_sha": self.local_head,
            "repository": {
                "repository_id": repository_id,
                "remote": self.remote_url,
                "branch": self.branch,
                "worktree": str(config.repository_path.resolve()),
                "protected_rollback_sha": config.protected_rollback_sha,
            },
            "prd": {
                "identity": "GACM_IMPLEMENTATION_PRD_V1.0.md",
                "content_sha": prd_sha,
            },
        }

    @staticmethod
    def _git_hash_object(repository_path: Path, path: Path) -> str:
        completed = subprocess.run(
            ["git", "hash-object", "--", str(path)],
            cwd=repository_path,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise ValueError("could not hash authoritative PRD")
        return completed.stdout.strip()


class AuthorityResolver:
    """Resolve one repository/ref into VERIFIED, BLOCKED, or AMBIGUOUS."""

    def __init__(self, config: ResolverConfig):
        self.config = config
        self.repository_path = config.repository_path.resolve()

    def resolve(self) -> ResolutionResult:
        result = ResolutionResult(
            status="BLOCKED",
            remote_name=self.config.remote_name,
            remote_ref=self.config.remote_ref(),
            authority_files=list(self.config.required_authority_files),
        )
        if not self.repository_path.is_dir():
            result.blocking_reasons.append("repository path does not exist or is not a directory")
            return result

        try:
            result.remote_url = self._git("remote", "get-url", self.config.remote_name).strip()
            result.repository = repository_identity(result.remote_url)
        except GitAuthorityError as error:
            result.blocking_reasons.append(str(error))
            return result

        if self.config.expected_repository is not None:
            result.repository_identity_match = result.repository == self.config.expected_repository
            if not result.repository_identity_match:
                result.blocking_reasons.append("repository identity does not match expected repository")
        else:
            result.repository_identity_match = True

        try:
            result.branch = self._git("branch", "--show-current").strip()
            result.local_head = self._git("rev-parse", "HEAD").strip()
        except GitAuthorityError as error:
            result.blocking_reasons.append(str(error))
            return result

        if result.branch != self.config.intended_branch:
            result.blocking_reasons.append("current branch is not the governed target branch")
        if not SHA_RE.fullmatch(result.local_head):
            result.blocking_reasons.append("local HEAD is not a full commit SHA")

        status = self._git_optional("status", "--porcelain", "--untracked-files=all")
        if status is None:
            result.blocking_reasons.append("could not establish worktree status")
        else:
            result.worktree_clean = status == ""
            if not result.worktree_clean:
                result.blocking_reasons.append("worktree is dirty and clean state is required")

        for authority_file in self.config.required_authority_files:
            if not (self.repository_path / authority_file).is_file():
                result.missing_authority_files.append(authority_file)
        if result.missing_authority_files:
            result.blocking_reasons.append("required authority files are missing")

        remote_heads = self._remote_heads()
        if len(remote_heads) == 0:
            result.ambiguous_reasons.append("intended remote ref has no uniquely resolvable HEAD")
        elif len(remote_heads) > 1:
            result.ambiguous_reasons.append("intended remote ref resolved to multiple HEADs")
        else:
            result.remote_head = remote_heads[0]
            if self.config.authorized_head is not None:
                result.authorized_head_match = result.remote_head == self.config.authorized_head
                if not result.authorized_head_match:
                    result.blocking_reasons.append("remote HEAD differs from required authorized HEAD")
            else:
                result.authorized_head_match = True
            if self._fetch_remote_ref():
                self._set_divergence(result)
            else:
                result.blocking_reasons.append("could not materialize remote ref for divergence proof")

        if result.local_head and result.remote_head:
            result.local_matches_remote = result.local_head == result.remote_head
            if not result.local_matches_remote:
                result.blocking_reasons.append("local HEAD does not match remote branch HEAD")

        if result.ambiguous_reasons and not result.blocking_reasons:
            result.status = "AMBIGUOUS"
        elif result.blocking_reasons or result.ambiguous_reasons:
            result.status = "BLOCKED"
        else:
            result.status = "VERIFIED"
        return result

    def _remote_heads(self) -> list[str]:
        completed = subprocess.run(
            ["git", "ls-remote", "--heads", self.config.remote_name, self.config.remote_ref()],
            cwd=self.repository_path,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            self._remote_error = completed.stderr.strip() or "remote ref lookup failed"
            return []
        heads: list[str] = []
        for line in completed.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 2 and SHA_RE.fullmatch(parts[0]):
                heads.append(parts[0])
        return heads

    def _set_divergence(self, result: ResolutionResult) -> None:
        if result.local_head == result.remote_head:
            result.divergence = "MATCH"
            return
        local_ancestor = self._is_ancestor(result.local_head, result.remote_head)
        remote_ancestor = self._is_ancestor(result.remote_head, result.local_head)
        if local_ancestor is True and remote_ancestor is False:
            result.divergence = "BEHIND"
        elif remote_ancestor is True and local_ancestor is False:
            result.divergence = "AHEAD"
        elif local_ancestor is False and remote_ancestor is False:
            result.divergence = "DIVERGED"
        else:
            result.divergence = "UNKNOWN"

    def _fetch_remote_ref(self) -> bool:
        """Materialize the exact remote commit for ancestry proof.

        This updates Git's object database/FETCH_HEAD only; it never updates the
        checked-out branch, worktree, or application files.
        """

        completed = subprocess.run(
            ["git", "fetch", "--no-tags", self.config.remote_name, self.config.remote_ref()],
            cwd=self.repository_path,
            text=True,
            capture_output=True,
            check=False,
        )
        return completed.returncode == 0

    def _is_ancestor(self, ancestor: str | None, descendant: str | None) -> bool | None:
        if not ancestor or not descendant:
            return None
        completed = subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor, descendant],
            cwd=self.repository_path,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode == 0:
            return True
        if completed.returncode == 1:
            return False
        return None

    def _git(self, *args: str) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=self.repository_path,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            detail = completed.stderr.strip() or "git command failed"
            raise GitAuthorityError(f"git {' '.join(args)}: {detail}")
        return completed.stdout

    def _git_optional(self, *args: str) -> str | None:
        completed = subprocess.run(
            ["git", *args],
            cwd=self.repository_path,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            return None
        return completed.stdout


def repository_identity(remote_url: str) -> str:
    """Return a stable owner/repository identity where the URL provides one."""

    value = remote_url.strip()
    if value.startswith("git@") and ":" in value:
        value = value.split(":", 1)[1]
    else:
        parsed = urlparse(value)
        if parsed.netloc:
            value = parsed.path.lstrip("/")
    if value.endswith(".git"):
        value = value[:-4]
    return value.rstrip("/")
