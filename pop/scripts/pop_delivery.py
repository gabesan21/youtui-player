#!/usr/bin/env python3
"""Mechanical external-yolo delivery: task→current branch and on-demand PR."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import poplib


def git(repo: Path, *args):
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True)


def repo_for(project: Path, explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).resolve()
    if (project / ".git").exists():
        return project
    raise RuntimeError("ambiguous repository: use --repo DIR")


def ensure_clean(repo: Path):
    status = git(repo, "status", "--porcelain")
    if status.returncode or status.stdout.strip():
        raise RuntimeError("working tree is not clean")


def integrate(repo: Path, task_id: str, dry_run: bool) -> str:
    ensure_clean(repo)
    branch = git(repo, "branch", "--show-current").stdout.strip()
    if not branch:
        raise RuntimeError("detached HEAD: yolo integration requires a "
                           "current working branch")
    task_branch = f"task/{task_id}"
    exists = git(repo, "show-ref", "--verify", f"refs/heads/{task_branch}")
    if exists.returncode:
        raise RuntimeError(f"missing branch: {task_branch}")
    ancestor = git(repo, "merge-base", "--is-ancestor", task_branch, branch)
    if ancestor.returncode == 0:
        return git(repo, "rev-parse", branch).stdout.strip()
    if dry_run:
        return f"dry-run: git merge --no-ff {task_branch}"
    merged = git(repo, "merge", "--no-ff", "--no-edit", task_branch)
    if merged.returncode:
        git(repo, "merge", "--abort")
        detail = (merged.stderr or merged.stdout).strip()
        raise RuntimeError(f"integration conflict/failure: {detail}")
    return git(repo, "rev-parse", "HEAD").stdout.strip()


def final_pr(repo: Path, base: str, dry_run: bool) -> str:
    ensure_clean(repo)
    head = git(repo, "branch", "--show-current").stdout.strip()
    if not head:
        raise RuntimeError("detached HEAD: the final PR requires a current "
                           "working branch")
    if shutil.which("gh") is None:
        raise RuntimeError("missing `gh` tool")
    existing = subprocess.run(
        ["gh", "pr", "list", "--base", base, "--head", head,
         "--state", "open", "--json", "url", "--jq", ".[0].url"],
        cwd=repo, capture_output=True, text=True)
    if existing.returncode == 0 and existing.stdout.strip():
        return existing.stdout.strip()
    if dry_run:
        return f"dry-run: gh pr create --base {base} --head {head}"
    created = subprocess.run(
        ["gh", "pr", "create", "--base", base, "--head", head,
         "--title", "PoP yolo delivery",
         "--body", "Delivery integrated and verified by the PoP yolo flow."],
        cwd=repo, capture_output=True, text=True)
    if created.returncode:
        raise RuntimeError((created.stderr or created.stdout).strip())
    return created.stdout.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    merge = sub.add_parser("integrate")
    merge.add_argument("task_id")
    merge.add_argument("--repo")
    merge.add_argument("--dry-run", action="store_true")
    merge.add_argument("--scope", "--vault", dest="vault")
    pr = sub.add_parser("scope-pr")
    pr.add_argument("--repo", default=".")
    pr.add_argument("--base", default="main",
                    help="PR target branch (default: main)")
    pr.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "scope-pr":
            print(final_pr(Path(args.repo).resolve(), args.base, args.dry_run))
            return 0
        root = poplib.vault_root(args.vault)
        found = poplib.find_task(root, args.task_id)
        if not found:
            raise RuntimeError(f"task not found: {args.task_id}")
        project, _stage, task_dir = found
        meta = poplib.read_card(task_dir / f"{args.task_id}.md")
        route = poplib.delivery_route(root, project, yolo=meta.get("yolo") is True)
        if not route["worktree"]:
            raise RuntimeError("a local scope delivers directly to main")
        if meta.get("yolo") is not True:
            raise RuntimeError("integrate is only for an external yolo task")
        print(integrate(repo_for(project, args.repo), args.task_id, args.dry_run))
        return 0
    except RuntimeError as error:
        print(f"aborted: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
