"""CLI for deterministic GACM Git authority resolution."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .resolver import AuthorityResolver, ResolverConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Resolve GACM Git authority deterministically")
    parser.add_argument("--repo", required=True, type=Path, help="repository worktree")
    parser.add_argument("--branch", required=True, help="governed local branch")
    parser.add_argument("--remote", default="origin", help="Git remote name")
    parser.add_argument("--ref", dest="intended_ref", help="exact remote ref; defaults to refs/heads/BRANCH")
    parser.add_argument("--expected-repository", help="expected normalized owner/repository identity")
    parser.add_argument("--authorized-head", help="required remote branch SHA")
    parser.add_argument("--protected-rollback-sha", help="known-good rollback SHA for run-state projection")
    parser.add_argument(
        "--required-file",
        action="append",
        dest="required_files",
        help="required authority file relative to repository; repeatable",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    config = ResolverConfig(
        repository_path=args.repo,
        intended_branch=args.branch,
        remote_name=args.remote,
        intended_ref=args.intended_ref,
        expected_repository=args.expected_repository,
        authorized_head=args.authorized_head,
        required_authority_files=tuple(args.required_files or ResolverConfig.required_authority_files),
        protected_rollback_sha=args.protected_rollback_sha,
    )
    result = AuthorityResolver(config).resolve()
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
