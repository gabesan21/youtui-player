#!/usr/bin/env python3
"""Installs and **updates** the standalone harness of a uni-repo repository.

The root PoP is the single source of the harness: no project evolves the
WORKFLOW, the templates or the scripts on its own — it receives a managed copy
of them. So that "update" is verifiable, every installation stamps the source's
`content_sha` of the managed set into `pop/.unirepo-harness.json`;
`--check-fresh` recomputes it and fails closed when the target has fallen
behind. Without the stamp there is no way to tell a current clone from a clone
stuck on an old version of the flow.

Manifest (`harness_root: "pop"`): files/directories/anatomy/keep_files are
relative to harness_root and go into `target/pop/`; `root_files`, skills,
AGENTS.md and CLAUDE.md stay at the target root. `.unirepo-harness.json` also
lives in `pop/` — it is the only recognized marker (with no legacy-layout
fallback) and it is what `poplib.vault_root` and `pop_validate --standalone`
use to detect the installed scope.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parent.parent
MANIFEST = SOURCE / "_templates" / "unirepo-manifest.json"
SKILLS_SOURCE = (SOURCE.parent / ".agents" / "skills"
                 if (SOURCE / ".unirepo-harness.json").is_file()
                 else SOURCE / ".agents" / "skills")
EXTERNAL_LINK = re.compile(r"\[\[projects/[^/]+/([^\]|#]+)([^\]]*)\]\]")
# Manifest fallback: the target gets the harness, not the parent's tooling.
DEFAULT_EXCLUDE = ("__pycache__", "tests", ".pytest_cache")


def root_source(name: str) -> Path:
    """Resolve a root artifact both at the origin and in an installed copy."""
    base = SOURCE.parent if (SOURCE / ".unirepo-harness.json").is_file() else SOURCE
    return base / name


def manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def excluded(data, relative: Path, label: str = "") -> bool:
    """A path the installer does not propagate.

    Two lists, two reasons. `exclude` drops noise by folder name (bytecode,
    the source's own test suite). `exclude_files` drops, by exact label,
    material that **only exists for whoever hosts other projects** —
    aggregation indexes, project creation, cross-scope overview. It is not
    omitted to save space: were it to reach the target, the installed harness
    would again describe a world above its own root.
    """
    names = set(data.get("exclude", DEFAULT_EXCLUDE))
    if names.intersection(relative.parts):
        return True
    if not label:
        return False
    if label in set(data.get("exclude_files", ())):
        return True
    return any(label == prefix or label.startswith(prefix + "/")
               for prefix in data.get("exclude_prefixes", ()))


def installed_manifest(data: dict) -> dict:
    """Return the target-facing manifest without origin-only exclusions."""
    return {key: value for key, value in data.items()
            if key != "exclude_prefixes"}


def managed_sources(data):
    """`(stable label, file)` for everything the installer propagates.

    The label is independent of the target's layout, so the `content_sha` only
    changes when the harness's **content** changes — not when the destination
    changes.
    """
    for name in data["files"]:
        yield name, SOURCE / name
    for name in data["directories"]:
        base = SOURCE / name
        for path in sorted(base.rglob("*")):
            relative = path.relative_to(base)
            label = f"{name}/{relative.as_posix()}"
            if path.is_file() and not excluded(data, relative, label):
                yield label, path
    for name in data.get("root_files", []):
        yield f"root/{name}", root_source(name)
    for name in data["skills"]:
        base = SKILLS_SOURCE / name
        for path in sorted(base.rglob("*")):
            relative = path.relative_to(base)
            label = f"skills/{name}/{relative.as_posix()}"
            if path.is_file() and not excluded(data, relative, label):
                yield label, path
    yield "manifest", MANIFEST


def content_sha(data=None) -> str:
    """Fingerprint of the harness at the source — the real version number."""
    data = data or manifest()
    digest = hashlib.sha256()
    for label, path in sorted(managed_sources(data)):
        digest.update(label.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def installed_stamp(target: Path, key: str = "content_sha"):
    """`(marker path, recorded field)` of the target; `None` if absent."""
    marker = target / "pop" / ".unirepo-harness.json"
    if not marker.is_file():
        return None, None
    try:
        return marker, json.loads(marker.read_text(encoding="utf-8")).get(key)
    except json.JSONDecodeError:
        return marker, None


def is_vendored() -> bool:
    """This script is the copy installed in a scope, not the original.

    The copy cannot **compare** versions: its `SOURCE` is the local harness,
    already localized at install time, so the hash never matches the origin's.
    It answers what it knows about itself — the stamped version — and stops
    there. Sending it to look for the origin would turn a local question into
    a boundary crossing.
    """
    return (SOURCE / ".unirepo-harness.json").is_file()


def localize(text: str, *, harness_paths: bool = False) -> str:
    """Strips the `projects/<project>/` prefix from the wikilinks of a uni-repo."""
    rendered = EXTERNAL_LINK.sub(
        lambda m: "[[" + m.group(1) + m.group(2) + "]]", text)
    if harness_paths:
        rendered = re.sub(r"(?<!pop/)scripts/", "pop/scripts/", rendered)
    return rendered


def copy_file(source: Path, dest: Path, *, overwrite: bool = True,
              harness_paths: bool = False) -> None:
    if dest.exists() and dest.is_dir():
        raise RuntimeError(f"collision with directory: {dest}")
    if dest.exists() and not overwrite:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    if source.suffix in {".md", ".py", ".json"}:
        if source.resolve() == MANIFEST.resolve():
            text = json.dumps(installed_manifest(manifest()), indent=2,
                              ensure_ascii=False) + "\n"
        else:
            text = source.read_text(encoding="utf-8")
        dest.write_text(localize(text, harness_paths=(harness_paths and source.suffix == ".md")),
                        encoding="utf-8")
    else:
        shutil.copy2(source, dest)


def copy_tree(source: Path, dest: Path, *, harness_paths: bool = False,
              data=None, label_prefix: str = "") -> list:
    """Copies `source` into `dest` and returns the files it wrote.

    It does not scan the destination: a managed folder is **not** an exclusive
    folder. The project legitimately keeps files of its own in `pop/scripts/`
    (its own verification, fixtures), and deleting everything that does not
    come from the source destroys the project's work. The pruning is driven by
    the previous installation's inventory — see `prune`.
    """
    data = data or manifest()
    written = []
    for path in source.rglob("*"):
        relative = path.relative_to(source)
        label = f"{label_prefix}{relative.as_posix()}" if label_prefix else ""
        if path.is_dir() or excluded(data, relative, label):
            continue
        target_file = dest / relative
        copy_file(path, target_file, harness_paths=harness_paths)
        written.append(target_file)
    return written


def prune(target: Path, previous, written) -> list:
    """Removes what the previous installation brought and this one no longer does.

    Only files the **installer itself** wrote before are candidates: it is the
    only way to retire a template or a script without touching what belongs to
    the project. With no previous inventory, nothing is removed.
    """
    removed = []
    for rel in sorted(set(previous) - {str(p) for p in written}, reverse=True):
        path = target / rel
        if not path.is_file():
            continue
        path.unlink()
        removed.append(rel)
        parent = path.parent
        while parent != target and parent.is_dir() and not any(parent.iterdir()):
            parent.rmdir()
            parent = parent.parent
    return removed


def preserve_worktree_marker(target: Path, prefix: str = "") -> None:
    """Allows versioning just the marker, even in repos that ignore worktrees/,
    and keeps the installed scripts' bytecode out of Git.
    `prefix` is the harness_root with a trailing slash (`pop/`) in the new anatomy."""
    ignore = target / ".gitignore"
    if not ignore.exists():
        return
    wt = f"{prefix}worktrees"
    block = (f"# unirepo-harness: preserve the standalone anatomy in Git\n"
             f"!{wt}/\n{wt}/*\n!{wt}/.gitkeep\n")
    text = ignore.read_text(encoding="utf-8")
    if f"!{wt}/.gitkeep" not in text:
        text = text.rstrip() + "\n\n" + block
    if "__pycache__/" not in text:
        text = (text.rstrip() +
                "\n# unirepo-harness: scripts' bytecode\n__pycache__/\n")
    ignore.write_text(text, encoding="utf-8")


# Terms describing a world **above** the target's root. If any reaches the
# target, the installed harness goes back to teaching the agent to climb — the
# very failure that `exclude_files` and this guard exist to prevent. The gate
# is about text the agent reads as instruction.
BOUNDARY_TOKENS = ("vault", "projects/", "meta-project", "root pop",
                   "parent pop", "parent vault", "drafts/", "hosting scope's",
                   "aggregated repositories", "parent project")
# In code, an identifier or a glob is not an instruction: `vault_root`,
# `--vault` and the `projects/*` pattern are internal mechanics and stay.
# What is banned is **text spoken to the agent** telling it to leave the scope.
BOUNDARY_TOKENS_CODE = ("meta-project", "root pop", "parent pop", "parent vault")


def _spoken_strings(source: str):
    """Literals the script **says** to the user: print, help= and errors."""
    import ast
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        target = node.func
        name = getattr(target, "id", None) or getattr(target, "attr", None)
        spoken = name in {"print", "error", "RuntimeError", "ValueError",
                          "SystemExit", "append"}
        for argument in (node.args if spoken else []):
            for piece in ast.walk(argument):
                if isinstance(piece, ast.Constant) and isinstance(piece.value, str):
                    yield piece.value
        for keyword in node.keywords:
            if keyword.arg != "help":
                continue
            for piece in ast.walk(keyword.value):
                if isinstance(piece, ast.Constant) and isinstance(piece.value, str):
                    yield piece.value


def boundary_violations() -> list[str]:
    """Managed labels that name something outside the target's scope.

    Fail closed: installing a harness that describes its host is the defect,
    not a wording detail. The target should not even have the vocabulary to
    describe whoever installed it.
    """
    data = manifest()
    found = []
    for label, path in sorted(managed_sources(data)):
        if path.suffix not in {".md", ".py"}:
            continue
        # Audit what **reaches** the target: `localize` already rewrites the
        # `projects/<project>/`-prefixed wikilinks, so failing on them is a
        # false positive.
        text = localize(path.read_text(encoding="utf-8"),
                        harness_paths=path.suffix == ".md")
        if path.suffix == ".md":
            haystacks, tokens = [text], BOUNDARY_TOKENS
        else:
            haystacks, tokens = list(_spoken_strings(text)), BOUNDARY_TOKENS_CODE
        hits = sorted({token for token in tokens
                       for hay in haystacks if token in hay.lower()})
        if hits:
            found.append(f"{label}: {', '.join(hits)}")
    return found


def audit() -> list[str]:
    data = manifest()
    missing = []
    for name in data["files"]:
        if not (SOURCE / name).is_file(): missing.append(name)
    for name in data["directories"]:
        if not (SOURCE / name).is_dir(): missing.append(name)
    for name in data.get("root_files", []):
        if not root_source(name).is_file(): missing.append(f"root:{name}")
    for name in data["skills"]:
        if not (SKILLS_SOURCE / name / "SKILL.md").is_file(): missing.append(f"skill:{name}")
    return missing


def preflight_root_files(target: Path, data: dict, previous: list[str]) -> None:
    """Refuse unmanaged root-file collisions before writing anything."""
    managed_before = set(previous)
    collisions = []
    for name in data.get("root_files", []):
        destination = target / name
        if destination.is_symlink():
            collisions.append(name)
        elif destination.exists() and name not in managed_before:
            collisions.append(name)
    if collisions:
        raise RuntimeError("collision with unmanaged root_file: " + ", ".join(collisions))


def install(target: Path) -> None:
    target = target.resolve()
    if not target.is_dir():
        raise RuntimeError(f"target is not a directory: {target}")
    missing = audit()
    if missing:
        raise RuntimeError("incomplete manifest: " + ", ".join(missing))
    leaks = boundary_violations()
    if leaks:
        raise RuntimeError("managed set names the hosting scope: "
                           + "; ".join(leaks))
    data = manifest()
    # harness_root: "pop" in the current manifest.
    hr = data.get("harness_root", "") or ""
    hb = target / hr if hr else target
    _, previous = installed_stamp(target, key="installed")
    preflight_root_files(target, data, previous or [])
    # Preflight: only explicitly managed paths may be written.
    written = []
    for name in data["files"]:
        copy_file(SOURCE / name, hb / name, harness_paths=True)
        written.append(hb / name)
    for name in data["directories"]:
        written += copy_tree(SOURCE / name, hb / name, harness_paths=True,
                             data=data, label_prefix=f"{name}/")
    for name in data.get("root_files", []):
        destination = target / name
        copy_file(root_source(name), destination, harness_paths=True)
        written.append(destination)
    for name in data["skills"]:
        written += copy_tree(SKILLS_SOURCE / name,
                             target / ".agents/skills" / name,
                             harness_paths=True, data=data,
                             label_prefix=f"skills/{name}/")
    inventory = sorted(path.relative_to(target).as_posix() for path in written)
    prune(target, previous or [], [path.relative_to(target).as_posix()
                                   for path in written])
    # The marker is the manifest plus this installation's content stamp and
    # inventory — the inventory is what authorizes the next one's pruning.
    stamp = dict(installed_manifest(data), content_sha=content_sha(data),
                 installed=inventory)
    (hb / ".unirepo-harness.json").write_text(
        json.dumps(stamp, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for rel in data["anatomy"]:
        (hb / rel).mkdir(parents=True, exist_ok=True)
    # Git does not preserve empty directories: these markers are a managed part
    # of the contract, so that a real clone keeps the whole standalone anatomy.
    for rel in data.get("keep_files", []):
        marker = hb / rel
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.touch()
    preserve_worktree_marker(target, f"{hr}/" if hr else "")
    # AGENTS belongs to the project: we never replace it. We only fix parent links.
    for path in target.rglob("*.md"):
        if ".git" in path.parts or "kanban" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        rendered = localize(text)
        if rendered != text:
            path.write_text(rendered, encoding="utf-8")
    agents = target / "AGENTS.md"
    if not agents.exists():
        copy_file(SOURCE / "_templates/AGENTS-PROJECT.md", agents)
    claude = target / "CLAUDE.md"
    if not claude.exists():
        claude.symlink_to("AGENTS.md")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?", type=Path)
    parser.add_argument("--check", action="store_true",
                        help="is the harness installed in the target?")
    parser.add_argument("--check-fresh", action="store_true",
                        help="is the target's harness at the source's version?")
    parser.add_argument("--audit-manifest", action="store_true")
    parser.add_argument("--audit-boundary", action="store_true",
                        help="is the managed set free of the hosting scope?")
    parser.add_argument("--sha", action="store_true",
                        help="print the content_sha of the harness at the source")
    args = parser.parse_args()
    missing = audit()
    if args.audit_manifest:
        if missing:
            print("incomplete manifest: " + ", ".join(missing), file=sys.stderr); return 1
        print("manifest complete"); return 0
    if args.audit_boundary:
        leaks = boundary_violations()
        if leaks:
            print("managed set names the hosting scope:", file=sys.stderr)
            for leak in leaks:
                print(f"  {leak}", file=sys.stderr)
            return 1
        print("boundary intact"); return 0
    if (args.sha or args.check_fresh) and is_vendored():
        # A local, complete answer. Comparing against the origin is the job of
        # whoever installed it; the scope does not leave to find that out.
        _, stamped = installed_stamp(SOURCE.parent)
        version = stamped[:12] if stamped else "unstamped"
        print(f"harness installed at version {version} — comparing against the "
              f"origin is done by whoever installed it, not by this scope")
        return 0
    if args.sha:
        print(content_sha()); return 0
    if not args.target:
        parser.error("target is required")
    if args.check:
        marker, _ = installed_stamp(args.target)
        if missing or marker is None:
            print("incomplete harness", file=sys.stderr); return 1
        print("harness installed"); return 0
    if args.check_fresh:
        if missing:
            print("incomplete manifest: " + ", ".join(missing), file=sys.stderr)
            return 1
        marker, stamped = installed_stamp(args.target)
        if marker is None:
            print(f"harness absent in {args.target}", file=sys.stderr); return 1
        current = content_sha()
        if stamped is None:
            print(f"harness without a stamp in {marker} — installed before "
                  f"content_sha; reinstall to date it", file=sys.stderr)
            return 1
        if stamped != current:
            print(f"harness STALE in {args.target}: target {stamped[:12]} "
                  f"≠ source {current[:12]} — run "
                  f"`pop_install_unirepo.py {args.target}`", file=sys.stderr)
            return 1
        print(f"harness current ({current[:12]})"); return 0
    try:
        install(args.target)
    except RuntimeError as error:
        print(f"aborted: {error}", file=sys.stderr); return 1
    print(f"standalone harness installed at {args.target}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
