#!/usr/bin/env python3
"""Keeps epoch and modification files with only still-open tasks.

`close <id>` is the closing operation of 005_closing: it requires a valid
canonical memory in the same scope and removes only the task's row — in
`roadmap/*.md` or `modifications/*.md` — or, for a single-task modification,
only the `[[M-N.T-slug]]` wikilink of the matching `MODIFICATIONS.md` line (the
modification's row stays). Epochs, phases and modifications are never
removed. `prune --tracked-only` is the safe migration: it removes rows whose
memory file is already tracked in Git. `check` lists leftovers without
editing.
"""

from __future__ import annotations

import argparse
import datetime
import re
import subprocess
import sys
from pathlib import Path

import poplib

TASK_ID = re.compile(
    r"(?<![0-9.])([0-9]+\.[0-9]+\.[0-9]+-[a-z0-9][a-z0-9-]*"
    r"|M-[0-9]+\.[0-9]+-[a-z0-9][a-z0-9-]*)")
ROW = re.compile(r"^\s*\|.*\|\s*$")
REQUIRED_MEMORY = ("task", "project", "started", "finished", "commit")
# `memory/` date folder: it is what groups the ledger with its entries.
MEMORY_DATE_DIR = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Folders with task rows removable by close: epochs and multi-task
# modifications. The MODIFICATIONS.md index gets its own handling (only the
# task's wikilink leaves the row).
ROW_DIRS = ("roadmap", "modifications")


def task_from_row(line: str) -> str | None:
    if not ROW.match(line):
        return None
    match = TASK_ID.search(line)
    return match.group(1) if match else None


def memory_ledgers(scope: Path, task_id: str) -> list[Path]:
    """Ledgers of `task_id` in the scope, date-folder layout first.

    New: `memory/<YYYY-MM-DD>/<id>.md`, with the folder equal to the ledger's
    own `finished`. Legacy: flat `memory/<id>.md` — tolerated only for memory
    predating the adoption (see `MEMORY_LAYOUT_SINCE` in `pop_validate`), and
    therefore still resolved here. More than one ledger for the same id is
    ambiguity, not "the first one found": the caller handles the list, not a
    single path.
    """
    base = poplib.harness_root(scope) / "memory"
    found = [path for path in sorted(base.glob(f"*/{task_id}.md"))
             if MEMORY_DATE_DIR.match(path.parent.name)]
    legacy = base / f"{task_id}.md"
    if legacy.is_file():
        found.append(legacy)
    return found


def memory_path(root: Path, scope: Path, task_id: str) -> Path:
    """The ledger's path; if none exists, the canonical one of the new layout —
    the path only serves as a message when there is no file, and the folder's
    date is precisely what is not known yet."""
    found = memory_ledgers(scope, task_id)
    if found:
        return found[0]
    return poplib.harness_root(scope) / "memory" / f"{task_id}.md"


def memory_valid(root: Path, scope: Path, task_id: str, *, canonical: bool) -> bool:
    found = memory_ledgers(scope, task_id)
    if len(found) != 1:
        return False  # absent, or ambiguous between layouts/dates
    path = found[0]
    if not canonical:
        return True
    meta, _ = poplib.parse_frontmatter(path.read_text(encoding="utf-8"))
    if any(meta.get(field) in (None, "") for field in REQUIRED_MEMORY):
        return False
    if "pr" not in meta:  # An explicit empty value is valid; a missing key is not.
        return False
    if meta.get("task") != task_id:
        return False
    # The label tells sibling projects apart, so it only makes sense when the
    # scope is a project **inside** an aggregating vault. In a standalone clone
    # the scope is the root itself: there the memory was written with the label
    # relative to the parent vault, which the clone has no way to reproduce —
    # demanding equality would make the repo unable to validate its own memories.
    if scope != root and meta.get("project") != poplib.project_label(root, scope):
        return False
    if scope == root and not meta.get("project"):
        return False
    try:
        started = datetime.date.fromisoformat(str(meta["started"]))
        finished = datetime.date.fromisoformat(str(meta["finished"]))
    except ValueError:
        return False
    # The date folder is the only thing that stops a decorative grouping: it
    # must be the completion date the ledger itself declares.
    if (MEMORY_DATE_DIR.match(path.parent.name)
            and path.parent.name != finished.isoformat()):
        return False
    return started <= finished


def tracked(root: Path, path: Path) -> bool:
    try:
        rel = path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--error-unmatch", rel.as_posix()],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    return result.returncode == 0


def task_rows(root: Path):
    """Table rows with a task id in roadmap/*.md and modifications/*.md."""
    for scope in poplib.discover_projects(root):
        harness = poplib.harness_root(scope)
        for folder in ROW_DIRS:
            base = harness / folder
            if not base.is_dir():
                continue
            for path in sorted(base.glob("*.md")):
                for number, line in enumerate(
                        path.read_text(encoding="utf-8").splitlines(), 1):
                    task_id = task_from_row(line)
                    if task_id:
                        yield scope, path, number, task_id


def modification_link_rows(root: Path):
    """[[M-N.T-slug]] wikilinks in MODIFICATIONS.md table rows.

    A single-task modification lives only in the index row; close removes
    only that wikilink (the modification's row stays).
    """
    link = re.compile(r"\[\[(M-[0-9]+\.[0-9]+-[a-z0-9][a-z0-9-]*)")
    for scope in poplib.discover_projects(root):
        index = poplib.harness_root(scope) / "MODIFICATIONS.md"
        if not index.is_file():
            continue
        for number, line in enumerate(
                index.read_text(encoding="utf-8").splitlines(), 1):
            if not ROW.match(line):
                continue
            for match in link.finditer(line):
                yield scope, index, number, match.group(1)


def residuals(root: Path, *, tracked_only: bool = False):
    rows = list(task_rows(root)) + list(modification_link_rows(root))
    for scope, path, number, task_id in rows:
        memory = memory_path(root, scope, task_id)
        if (memory_valid(root, scope, task_id, canonical=False)
                and (not tracked_only or tracked(root, memory))):
            yield scope, path, number, task_id


def _remove_row(matches, task_id: str) -> bool:
    """Removes the single `task_id` row among the origin files.

    Returns True when removed; False when no row was found. Raises
    RuntimeError when the task appears in more than one row (aborts without
    writing anything).
    """
    count = sum(len(indexes) for _, _, indexes in matches)
    if count == 0:
        return False
    if count != 1:
        raise RuntimeError(
            f"expected exactly 1 row for `{task_id}`, found {count}")
    path, lines, indexes = matches[0]
    remove_index = indexes[0]
    kept = lines[:remove_index] + lines[remove_index + 1:]
    path.write_text("\n".join(kept) + "\n", encoding="utf-8")
    return True


def _unlink_modification_index(harness: Path, task_id: str) -> None:
    """Single task: removes only the [[M-N.T-slug]] wikilink from the index row.

    The modification's row stays (status `completed`); the id returns to the
    backticked `` `M-N.T-slug` `` form, like a not-yet-linked task.
    """
    index = harness / "MODIFICATIONS.md"
    if not index.is_file():
        raise RuntimeError(
            f"no row for `{task_id}` in roadmap/modifications and "
            f"{index} is missing")
    lines = index.read_text(encoding="utf-8").splitlines()
    hits = [i for i, line in enumerate(lines)
            if ROW.match(line) and task_id in line]
    if len(hits) != 1:
        raise RuntimeError(
            f"expected exactly 1 row for `{task_id}` in {index}, "
            f"found {len(hits)}")
    pattern = re.compile(
        r"\[\[" + re.escape(task_id) + r"(?:\|[^\]]*)?\]\]")
    lines[hits[0]], count = pattern.subn(f"`{task_id}`", lines[hits[0]])
    if count != 1:
        raise RuntimeError(
            f"wikilink [[{task_id}]] not found in the row of {index}")
    index.write_text("\n".join(lines) + "\n", encoding="utf-8")


def remove_task(root: Path, scope: Path, task_id: str, *, canonical: bool,
                tracked_only: bool) -> int:
    memory = memory_path(root, scope, task_id)
    if not memory_valid(root, scope, task_id, canonical=canonical):
        raise RuntimeError(f"invalid or missing memory: {memory}")
    if tracked_only and not tracked(root, memory):
        raise RuntimeError(f"untracked memory: {memory}")
    harness = poplib.harness_root(scope)
    matches = []
    for folder in ROW_DIRS:
        base = harness / folder
        if not base.is_dir():
            continue
        for path in sorted(base.glob("*.md")):
            lines = path.read_text(encoding="utf-8").splitlines()
            indexes = [i for i, line in enumerate(lines)
                       if task_from_row(line) == task_id]
            if indexes:
                matches.append((path, lines, indexes))
    if not _remove_row(matches, task_id):
        _unlink_modification_index(harness, task_id)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "close", "prune"))
    parser.add_argument("task_id", nargs="?")
    parser.add_argument("--scope", "--vault", dest="vault", metavar="DIR")
    parser.add_argument("--tracked-only", action="store_true")
    args = parser.parse_args()
    root = poplib.vault_root(args.vault)

    if args.command == "check":
        found = list(residuals(root, tracked_only=args.tracked_only))
        for _, path, number, task_id in found:
            print(f"{path}:{number}: residual completed task `{task_id}`")
        return 1 if found else 0

    if args.command == "close":
        if not args.task_id:
            parser.error("close requires task_id")
        found = poplib.find_task(root, args.task_id)
        if not found:
            print(f"task not found in kanban: {args.task_id}", file=sys.stderr)
            return 1
        scope, stage, _ = found
        if stage != "005_closing":
            print(f"task must be in 005_closing, currently in {stage}",
                  file=sys.stderr)
            return 1
        targets = [(scope, args.task_id)]
        canonical = True
    else:
        targets = [(scope, task_id) for scope, _, _, task_id in residuals(
            root, tracked_only=args.tracked_only)]
        canonical = False

    try:
        for scope, task_id in targets:
            remove_task(root, scope, task_id, canonical=canonical,
                        tracked_only=args.tracked_only)
            print(f"OK: removed completed row `{task_id}`")
    except RuntimeError as error:
        print(f"aborted: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
