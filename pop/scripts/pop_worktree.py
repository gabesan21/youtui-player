#!/usr/bin/env python3

import argparse
import subprocess
import sys

import poplib


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True)


def fail(action, result):
    detail = (result.stderr or result.stdout).strip() or "no details"
    print(f"Failed to {action} (git exit {result.returncode}):\n  {detail}")
    return 1


def cmd_add(repo, worktree, branch, base, rel):
    if worktree.exists():
        print(f"Worktree already exists: {worktree}")
        return 1
    worktree.parent.mkdir(parents=True, exist_ok=True)
    args = ["worktree", "add", str(worktree), "-b", branch]
    if base:
        args.append(base)
    result = git(repo, *args)
    if result.returncode != 0:
        return fail(f"create worktree {worktree}", result)
    print(f"OK: worktree {worktree} created on branch {branch}"
          + (f" from {base}." if base else "."))
    print(f"Reminder: record `worktree: {rel}` in the card frontmatter.")
    return 0


def cmd_remove(repo, worktree, branch, force_delete):
    result = git(repo, "worktree", "remove", str(worktree))
    if result.returncode != 0:
        return fail(f"remove worktree {worktree}", result)
    print(f"OK: worktree {worktree} removed.")

    merged = git(repo, "branch", "--merged")
    is_merged = merged.returncode == 0 and any(
        line.strip().lstrip("* ") == branch
        for line in merged.stdout.splitlines())
    if is_merged or force_delete:
        flag = "-D" if force_delete else "-d"
        result = git(repo, "branch", flag, branch)
        if result.returncode != 0:
            return fail(f"delete branch {branch}", result)
        print(f"OK: branch {branch} deleted"
              + (" (forced)." if force_delete and not is_merged else "."))
    else:
        print(f"Branch {branch} kept (not merged — use --delete-branch "
              f"to force).")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Create or remove a task's Git worktree "
                    "(worktrees/<id>, branch task/<id>).")
    parser.add_argument("action", choices=["add", "remove", "route"],
                        help="add/remove: manage worktree; route: show Git route")
    parser.add_argument("task_id", help="task ID (kanban folder name)")
    parser.add_argument("--repo", metavar="DIR|NAME",
                        help="target Git repository: path or project clone name; "
                             "defaults to the project if it is a Git repository, "
                             "otherwise to the vault root")
    parser.add_argument("--base", metavar="BRANCH",
                        help="base branch for the new branch (add only)")
    parser.add_argument("--delete-branch", action="store_true",
                        help="on remove, delete the branch even if unmerged")
    parser.add_argument("--scope", "--vault", dest="vault", metavar="DIR",
                        help="vault root (default: directory above scripts/)")
    args = parser.parse_args()

    root = poplib.vault_root(args.vault)
    found = poplib.find_task(root, args.task_id)
    if not found:
        print(f"Task not found in any project: {args.task_id}")
        return 1
    project, stage, task_dir = found
    card = task_dir / f"{args.task_id}.md"
    meta = poplib.read_card(card)
    yolo = bool(meta.get("yolo"))
    route = poplib.delivery_route(root, project, yolo=yolo)
    print(f"Task {args.task_id} in {poplib.project_label(root, project)} "
          f"({stage}).")
    if args.action == "route":
        print(f"worktree={'yes' if route['worktree'] else 'no'}")
        print(f"integration_branch={route['task_branch'] or 'current'}")
        print(f"final_pr={'on-request' if yolo and route['worktree'] else 'yes' if route['scope_pr'] else 'no'}")
        print(f"target_branch={route['target_branch'] or ('on-request' if yolo else 'configured-in-project')}")
        print(f"merge_owner={route['merge_owner']}")
        return 0
    if not route["worktree"]:
        print("Operation refused: the local meta PoP works directly on main, "
              "without a task branch, worktree, or PR.")
        return 1

    worktree = poplib.harness_root(project) / "worktrees" / args.task_id
    if args.repo:
        # Project clone: `<name>/` in current anatomy, `project/<name>/` in legacy anatomy.
        embedded = project / args.repo
        if not embedded.is_dir():
            embedded = project / "project" / args.repo
        if "/" not in args.repo and embedded.is_dir():
            # Named project clone: one nested worktree per affected repository.
            repo = embedded
            worktree = worktree / args.repo
        else:
            repo = poplib.vault_root(args.repo)
    elif (project / ".git").exists():
        repo = project  # uni-repo project or multi-repo repository.
    else:
        repo = root
    if not (repo / ".git").exists():
        print(f"Not a git repository: {repo}")
        return 1
    branch = f"task/{args.task_id}"
    if args.action == "add":
        base = args.base
        if yolo:
            if not base:
                current = git(repo, "branch", "--show-current")
                base = current.stdout.strip()
                if current.returncode != 0 or not base:
                    print("Operation refused: the repo is on a detached HEAD; "
                          "an external yolo task needs a current working "
                          "branch (or an explicit --base).")
                    return 1
            print(f"Yolo route: worktree from {base} and integration back "
                  f"into it; final PR only on human request; merge by "
                  f"{route['merge_owner']}.")
        return cmd_add(repo, worktree, branch, base,
                       worktree.relative_to(project).as_posix())
    return cmd_remove(repo, worktree, branch, args.delete_branch)


if __name__ == "__main__":
    sys.exit(main())
