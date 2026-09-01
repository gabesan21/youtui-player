
from __future__ import annotations

import datetime
import getpass
import json
import re
import socket
from pathlib import Path
from typing import Iterator, Optional, Tuple

STAGES = [
    "001_initial_task",
    "002_planning",
    "003_human_approval",
    "004_processing",
    "005_closing",
]

DEFAULT_LEASE_HOURS = 2
YOLO_RETURN_LIMIT = 2

# Classification of the last return (`return_kind:` on the card, written only
# by pop_move). `lacuna` = incomplete plan, what was delivered is correct →
# amendment; `premissa` = wrong strategy → replanning; `execucao` = the
# executor did not meet the criteria it was given. It sizes the amendment and
# the mode of the re-review.
RETURN_KINDS = ("lacuna", "premissa", "execucao")

RELEASE_MARK = re.compile(r"^\s*[-*]\s*\[[xX]\]\s*Ready to plan")

# Judge Dredd machine markers in the `.verify.md` (see [[specs/judge-dredd]]).
# Every round ends with a `pop-verdict`; a return adds the same round's
# `pop-delta`. They are what `pop_move` and `pop_validate` read — the prose is
# for humans, the marker is the executable contract. `key=value` fields with
# no spaces; comma-separated lists (`paths=src/a.ts,tests/b.spec.ts`).
VERDICT_MARKER = re.compile(r"<!--\s*pop-verdict\s+([^>]*?)-->")
DELTA_MARKER = re.compile(r"<!--\s*pop-delta\s+([^>]*?)-->")
MARKER_FIELD = re.compile(r"([\w-]+)=([^\s>]+)")
# `aprovada` ends the gate (terminal); `reparo-dirigido` is not a route (the
# folder does not move); the three RETURN_KINDS are the return routes.
VERDICT_DECISIONS = ("aprovada", "reparo-dirigido") + RETURN_KINDS


def parse_verify_markers(text: str):
    """(verdicts, deltas) from a `.verify.md`'s machine markers.

    Verdicts come in file order (the last round decides); deltas are indexed
    by the declared `round`. Fields are raw strings — validating the enums is
    the caller's job.
    """
    verdicts = [dict(MARKER_FIELD.findall(m.group(1)))
                for m in VERDICT_MARKER.finditer(text)]
    deltas = {}
    for m in DELTA_MARKER.finditer(text):
        fields = dict(MARKER_FIELD.findall(m.group(1)))
        deltas[fields.get("round")] = fields
    return verdicts, deltas


def marker_paths(delta: dict) -> list:
    """List of paths from a pop-delta's `paths` field (empty when absent)."""
    return [p for p in (delta.get("paths") or "").split(",") if p]

def vault_root(override: Optional[str] = None) -> Path:
    """Root of the current scope.

    In an installed harness the scripts live in `pop/scripts/`: the root is
    the folder above `pop/`, and the search **stops there**. The marker is the
    boundary — no script walks past it looking for a larger scope, even when
    one exists on disk. An installed harness is a complete world.
    """
    if override:
        return Path(override).resolve()
    base = Path(__file__).resolve().parent.parent
    if base.name == "pop" and (base / ".unirepo-harness.json").is_file():
        return base.parent
    return base


def is_installed_scope(root: Path) -> bool:
    """The scope received its harness from an origin (it is not the origin).

    An installed scope hosts no other projects, keeps no aggregation indexes
    and does not answer for the origin's version.
    """
    return (root / "pop" / ".unirepo-harness.json").is_file()


def harness_root(project: Path) -> Path:
    return project / "pop" if (project / "pop" / "kanban").is_dir() else project


def templates_dir(root: Path) -> Path:
    new = root / "pop" / "_templates"
    return new if new.is_dir() else root / "_templates"


def today() -> str:
    return datetime.date.today().isoformat()


def _coerce(raw: str):
    raw = raw.strip()
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ("'", '"'):
        return raw[1:-1]
    if raw.lower() == "true":
        return True
    if raw.lower() == "false":
        return False
    if raw == "":
        return None
    return raw


def _parse_value(raw: str):
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return [_coerce(item) for item in inner.split(",")]
    return _coerce(raw)


def parse_frontmatter(text: str) -> Tuple[dict, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    meta: dict = {}
    current = None
    end = None
    for i in range(1, len(lines)):
        line = lines[i]
        if line.strip() == "---":
            end = i
            break
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- ") and current is not None:
            if not isinstance(meta[current], list):
                meta[current] = []
            meta[current].append(_coerce(stripped[2:]))
            continue
        if ":" in stripped and not line.startswith((" ", "\t")):
            key, _, raw = line.partition(":")
            current = key.strip()
            meta[current] = _parse_value(raw)
    if end is None:  # Unclosed frontmatter.
        return {}, text
    return meta, "\n".join(lines[end + 1:])


def discover_projects(root: Path) -> list:
    scopes = set()
    if (root / "kanban").is_dir() or (root / "pop" / "kanban").is_dir():
        scopes.add(root)
    patterns = (
        ("projects/*/pop/kanban", 2),      # uni-repo project.
        ("projects/*/*/pop/kanban", 2),    # multi-repo repository.
    )
    for pattern, up in patterns:
        for kanban in root.glob(pattern):
            if not kanban.is_dir():
                continue
            scope = kanban.parents[up - 1]
            rel = scope.relative_to(root)
            if any(part.startswith(".") for part in rel.parts):
                continue
            scopes.add(scope)
    return sorted(scopes)


# Harness traversal includes each multi-repo repository.
HARNESS_DIRS = ("roadmap", "specs", "researches", "skills", "notes",
                "memory", "open_questions", "drafts", "kanban")
HARNESS_ROOT_FILES = ("PROJECT.md", "ROADMAP.md")  # INDEX.md has its own 144/600 limit.
# Skip generated, vendored, and nested non-harness content.
_HARNESS_SKIP = {"raw", "worktrees", "_templates", "__pycache__",
                 "node_modules", "vendor", ".git", ".obsidian"}


def iter_harness_markdown(scope: Path) -> Iterator[Path]:
    hroot = harness_root(scope)
    for name in HARNESS_ROOT_FILES:
        if (hroot / name).is_file():
            yield hroot / name
    for name in HARNESS_DIRS:
        base = hroot / name
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.md")):
            if not (_HARNESS_SKIP & set(path.relative_to(hroot).parts)):
                yield path


def iter_all_harness_markdown(root: Path) -> Iterator[Path]:
    seen = set()
    for scope in discover_projects(root):
        for path in iter_harness_markdown(scope):
            if path not in seen:
                seen.add(path)
                yield path


def project_label(root: Path, project: Path) -> str:
    """Short name of a project folder.

    The root is only called `pop` when it is the scope hosting the others
    (kanban at the root itself). An installed scope also has `project ==
    root`, but reusing the label there would make its cards say
    `project: pop` and wrongly inherit the host's delivery route — it uses
    the name of its own root instead.
    """
    if project == root:
        return "pop" if (root / "kanban").is_dir() else root.name
    parts = project.relative_to(root / "projects").parts
    return "/".join(parts)


def project_dir(root: Path, label: str) -> Path:
    if label == project_label(root, root):
        return root
    parts = [p for p in label.split("/") if p]
    return root.joinpath("projects", *parts)


def delivery_route(root: Path, project: Path, *, yolo: bool) -> dict:
    if project.resolve() == root.resolve() and (root / "kanban").is_dir():
        return {"task_branch": "main", "scope_pr": False,
                "target_branch": "main", "worktree": False,
                "merge_owner": "none"}
    # External yolo: worktree and integration on the current working branch
    # (resolved at add/integrate time, hence task_branch=None); the final PR
    # exists only on explicit human request.
    if yolo:
        return {"task_branch": None, "scope_pr": False,
                "target_branch": None, "worktree": True,
                "merge_owner": "user"}
    return {"task_branch": "task", "scope_pr": False,
            "target_branch": None, "worktree": True,
            "merge_owner": "user"}


def iter_cards(project: Path) -> Iterator[Tuple[str, Path, Path]]:
    for stage in STAGES:
        stage_dir = harness_root(project) / "kanban" / stage
        if not stage_dir.is_dir():
            continue
        for task_dir in sorted(p for p in stage_dir.iterdir() if p.is_dir()):
            card = task_dir / f"{task_dir.name}.md"
            if card.is_file():
                yield stage, task_dir, card


def read_card(card: Path) -> dict:
    meta, _ = parse_frontmatter(card.read_text(encoding="utf-8"))
    return meta


def task_released(card: Path) -> bool:
    in_fence = False
    for line in card.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and RELEASE_MARK.match(line):
            return True
    return False


def default_agent() -> str:
    return f"{getpass.getuser()}@{socket.gethostname()}"


def now() -> datetime.datetime:
    return datetime.datetime.now().astimezone()


def telemetry_path(task_dir: Path) -> Path:
    """Ephemeral task sidecar; 005_closing summarizes and drops it with the card."""
    return task_dir / f"{task_dir.name}.telemetry.json"


def read_telemetry(task_dir: Path) -> dict:
    path = telemetry_path(task_dir)
    if not path.is_file():
        return {"version": 1, "events": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"version": 1, "events": []}
    if not isinstance(data, dict) or not isinstance(data.get("events"), list):
        return {"version": 1, "events": []}
    return data


def record_telemetry(task_dir: Path, event: dict) -> None:
    data = read_telemetry(task_dir)
    payload = {"at": now().isoformat(timespec="seconds"), **event}
    data["events"].append(payload)
    path = telemetry_path(task_dir)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")


def telemetry_summary(task_dir: Path) -> dict:
    events = read_telemetry(task_dir)["events"]
    contexts = sum(len(e.get("contexts") or []) for e in events)
    returns = {"003": 0, "005": 0}
    kinds = {kind: 0 for kind in RETURN_KINDS}
    test_seconds = 0.0
    for event in events:
        src, dst = event.get("from"), event.get("to")
        # Plan return: the 003 gate, or a plan defect caught in 005_closing.
        if dst == "002_planning" and src in ("003_human_approval", "005_closing"):
            returns["003"] += 1
        if src == "005_closing" and dst == "004_processing":
            returns["005"] += 1
        if event.get("return_kind") in kinds:
            kinds[event["return_kind"]] += 1
        test_seconds += float(event.get("test_seconds") or 0)
    duration = None
    if len(events) >= 2:
        try:
            start = datetime.datetime.fromisoformat(events[0]["at"])
            end = datetime.datetime.fromisoformat(events[-1]["at"])
            duration = int((end - start).total_seconds())
        except (KeyError, TypeError, ValueError):
            pass
    return {"duration_seconds": duration, "contexts": contexts,
            "returns_003": returns["003"], "returns_005": returns["005"],
            # Cause of the returns, to tell whether the bottleneck is plan or
            # execution.
            **{f"returns_{kind}": count for kind, count in kinds.items()},
            "test_seconds": test_seconds, "events": len(events)}


def parse_claim(meta: dict) -> Tuple[Optional[str], Optional[datetime.datetime]]:
    by = meta.get("claimed_by") or None
    raw = str(meta.get("claimed_at") or "")
    try:
        at = datetime.datetime.fromisoformat(raw)
        if at.tzinfo is None:
            at = at.astimezone()
    except ValueError:
        at = None
    return by, at


def claim_expired(at: Optional[datetime.datetime],
                  lease_hours: float = DEFAULT_LEASE_HOURS) -> bool:
    if at is None:
        return True  # A claim without a valid timestamp cannot hold a lease.
    return now() - at > datetime.timedelta(hours=lease_hours)


def find_task(root: Path, task_id: str):
    for project in discover_projects(root):
        kanban = harness_root(project) / "kanban"
        for stage in STAGES:
            task_dir = kanban / stage / task_id
            if task_dir.is_dir():
                return project, stage, task_dir
    return None
