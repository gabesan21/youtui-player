#!/usr/bin/env python3

import argparse
import datetime
import hashlib
import json
import re
import sys

import poplib
import pop_roadmap

MAX_ROOT_DESC = 144
MAX_NOTE_LINES = 150
MAX_PLAN_LINES = 80      # plan root (`<id>.plan.md`), regardless of size
MAX_FRONT_LINES = 50     # front file in `subtasks/`: one executor's slice
MAX_PROJECT_AGENTS = 60  # a project's AGENTS.md: a pointer, not a copy of the flow
# Caps of the quality-gate artifacts (see [[specs/judge-dredd]], table
# "Interfaces"). The key is the suffix of the **task** artifact, never a
# template name: `_templates/TASK-VERIFY.md` remains an ordinary 150-line note.
# The three artifacts of the adversarial gate retired on 2026-08-04 keep their
# caps because cards older than the cutoff may carry them as history; the
# `.r<n>` infix sits before the suffix, so `endswith` already reaches each
# round.
GATE_ARTIFACT_LIMITS = {
    ".verify.md": 80,       # Judge Dredd's judgment, all rounds
    ".defense.md": 30,      # history: the plan's contestable decisions
    ".accusation.md": 50,   # history: the devil's advocate objections
    ".judgment.md": 40,     # history: the judge's judgment and route
}
# Memory caps, in **characters**: memory is a ledger and entries, not a note,
# and what makes it optimizable by an agent is the file size, not the line
# count. The ledger is the proof (frontmatter, delivery, verification, index);
# an entry is one thing done, with linked evidence (see [[_templates/MEMORY]]
# and [[_templates/MEMORY-ENTRY]]). Memory is measured by `check_memory` —
# `note_limit` does not reach `memory/`.
MAX_MEMORY_LEDGER = 1200
MAX_MEMORY_ENTRY = 800
# Date on which the `memory/<YYYY-MM-DD>/` layout became mandatory. Flat memory
# older than it is tolerated legacy — that is what keeps `uni-repo` clones
# valid, whose memories this vault does not rewrite.
MEMORY_LAYOUT_SINCE = "2026-07-27"
MEMORY_DATE_DIR = pop_roadmap.MEMORY_DATE_DIR
# Entry: `<id>.<nn>-<slug>.md` in the same folder as the ledger `<id>.md`. The
# `.` reuses the kanban artifact convention (`<id>.plan.md`).
MEMORY_ENTRY_SUFFIX = re.compile(r"^\.(\d{2}-[a-z0-9][a-z0-9-]*)$")
VERIFY_ARTIFACT = ".verify.md"
# Artifacts of the adversarial gate retired on 2026-08-04: they are not born
# in a card created on or after the cutoff; in an older card they are
# tolerated history.
RETIRED_GATE_ARTIFACTS = (".defense.md", ".accusation.md", ".judgment.md")
# Round infix of the act-1 artifacts (`<id>.r<n>.<artifact>.md`): what decides
# the family is the suffix, never the round, so every check matches the name
# with and without the infix.
ROUND_INFIX = re.compile(r"\.r\d+$")
# Date on which the Judge Dredd (single judge) replaced the adversarial gate
# (see [[WORKFLOW]], act 1 of `005_closing`, "Transition"). A card with an
# earlier `created:` may carry defense/accusation/judgment as history.
JUDGE_DREDD_SINCE = "2026-08-04"
# An application embeds the DOX process and only for that exceeds the cap (rule 5).
DOX_MARKER = "DOX process"
EXEMPT_NAMES = {"AGENTS.md", "WORKFLOW.md", "README.md"}
CARD_REQUIRED = ("id", "project", "stage", "created", "updated")
ORIGIN_VALUES = ("roadmap", "modifications")
MODIFICATION_REF = re.compile(r"^M-\d+$")
SIZE_VALUES = {"S", "M", "L"}
SPEC_REQUIRED = (
    "id", "project", "domain", "kind", "status", "implementation",
    "origin", "created", "updated", "supersedes", "superseded_by",
)
SPEC_ENUMS = {
    "kind": {"contract", "overview"},
    "status": {"draft", "active", "superseded"},
    "implementation": {"planned", "partial", "implemented",
                       "not_applicable"},
}
KEBAB_CASE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

ROOT_ENTRY = re.compile(r"^- \[\[.*?\]\]\s*—\s*(.+)$")
TASK_DIR = re.compile(r"^(?:\d+\.\d+\.\d+|M-\d+\.\d+)-")
WIKILINK = re.compile(r"!?\[\[([^\]|#^]*)")
POP_HASH = re.compile(r"<!--\s*pop-hash:\s*(\S+)\s+sha256=([0-9a-fA-F]+)\s*-->")
INLINE_CODE = re.compile(r"`[^`]*`")
LINK_SKIP_PARTS = {"external-repository", ".obsidian", ".git", "worktrees",
                   "__pycache__", "node_modules", "vendor"}
# Suffixes of the task's own stage artifacts (created only as it advances in
# the kanban): a freshly created card links `.plan/.approval/.verify` that are
# not born yet — an expected navigation link, not a real break (see [[WORKFLOW]]).
# The act-1 artifacts carry a round infix (`<id>.r<n>.accusation`), which
# `_stage_artifact_base` strips from both sides of the comparison.
STAGE_ARTIFACT_SUFFIXES = (".plan", ".approval", ".verify",
                           ".defense", ".accusation", ".judgment")
EXTERNAL_PROJECT_LINK = re.compile(r"\[\[projects/[^/]+/")


def _spec_links(path):
    links = []
    for _, line in lines_outside_fences(path):
        for match in WIKILINK.finditer(INLINE_CODE.sub("", line)):
            target = match.group(1).strip().rstrip("\\").split("#", 1)[0]
            if target:
                links.append(target)
    return links


def _spec_aliases(root, specs_dir, path):
    rel_collection = path.relative_to(specs_dir).with_suffix("").as_posix()
    rel_root = path.relative_to(root).with_suffix("").as_posix()
    return {path.stem, rel_collection, rel_root}


def _linked_specs(root, specs_dir, source, documents):
    aliases = {}
    for path in documents:
        for alias in _spec_aliases(root, specs_dir, path):
            aliases.setdefault(alias, set()).add(path)
    resolved = set()
    for target in _spec_links(source):
        matches = aliases.get(target.removesuffix(".md"), set())
        if len(matches) == 1:
            resolved.update(matches)
    return resolved


def _valid_iso_date(value):
    raw = str(value or "")
    try:
        parsed = datetime.date.fromisoformat(raw)
    except ValueError:
        return None
    return parsed if parsed.isoformat() == raw else None


def check_spec_collections(root, projects, violations):
    for project in projects:
        specs_dir = poplib.harness_root(project) / "specs"
        index = specs_dir / "INDEX.md"
        if not index.is_file():
            continue

        documents = sorted(path for path in specs_dir.rglob("*.md")
                           if path != index)
        metadata = {}
        ids = {}
        expected_project = poplib.project_label(root, project)

        for path in documents:
            rel = path.relative_to(specs_dir)
            if len(rel.parts) > 2:
                violations.append(
                    f"{path}:1: spec nesting is invalid; use at most "
                    "`specs/<domain>/file.md`")

            meta, _ = poplib.parse_frontmatter(
                path.read_text(encoding="utf-8"))
            metadata[path] = meta
            for field in SPEC_REQUIRED:
                if field not in meta:
                    violations.append(
                        f"{path}:1: frontmatter missing `{field}`")
                elif (field not in {"supersedes", "superseded_by"}
                      and meta[field] in (None, "")):
                    violations.append(
                        f"{path}:1: frontmatter has empty `{field}`")

            spec_id = meta.get("id")
            if not isinstance(spec_id, str) or not KEBAB_CASE.fullmatch(spec_id):
                violations.append(f"{path}:1: `id` invalid `{spec_id}` "
                                  "(use kebab-case)")
            elif spec_id in ids:
                violations.append(f"{path}:1: duplicate `id` `{spec_id}` "
                                  f"(also in {ids[spec_id]})")
            else:
                ids[spec_id] = path

            # Same criterion as `memory_valid`: the label separates sibling
            # projects, so it only holds where siblings exist. In a standalone
            # clone (scope == root) the spec carries the parent vault's label,
            # which the clone does not reproduce — the field just has to be filled.
            if project == root:
                if not meta.get("project"):
                    violations.append(f"{path}:1: empty `project`")
            elif meta.get("project") != expected_project:
                violations.append(
                    f"{path}:1: `project` `{meta.get('project')}` differs from "
                    f"scope label `{expected_project}`")

            domain = meta.get("domain")
            if not isinstance(domain, str) or not KEBAB_CASE.fullmatch(domain):
                violations.append(f"{path}:1: `domain` invalid `{domain}` "
                                  "(use kebab-case)")
            elif len(rel.parts) == 2 and domain != rel.parts[0]:
                violations.append(
                    f"{path}:1: `domain` `{domain}` differs from folder "
                    f"`{rel.parts[0]}`")

            for field, accepted in SPEC_ENUMS.items():
                if meta.get(field) not in accepted:
                    options = " | ".join(sorted(accepted))
                    violations.append(
                        f"{path}:1: `{field}` invalid `{meta.get(field)}` "
                        f"(use {options})")

            created = _valid_iso_date(meta.get("created"))
            updated = _valid_iso_date(meta.get("updated"))
            if created is None:
                violations.append(f"{path}:1: `created` invalid "
                                  f"`{meta.get('created')}` (use YYYY-MM-DD)")
            if updated is None:
                violations.append(f"{path}:1: `updated` invalid "
                                  f"`{meta.get('updated')}` (use YYYY-MM-DD)")
            if created and updated and updated < created:
                violations.append(f"{path}:1: `updated` precedes `created`")

            supersedes_value = meta.get("supersedes")
            if not isinstance(supersedes_value, list):
                violations.append(f"{path}:1: `supersedes` must be a list")
            else:
                for old_id in supersedes_value:
                    if (not isinstance(old_id, str)
                            or not KEBAB_CASE.fullmatch(old_id)):
                        violations.append(
                            f"{path}:1: invalid ID in `supersedes`: "
                            f"`{old_id}`")

            replacement_value = meta.get("superseded_by")
            if (replacement_value is not None
                    and (not isinstance(replacement_value, str)
                         or not KEBAB_CASE.fullmatch(replacement_value))):
                violations.append(
                    f"{path}:1: `superseded_by` invalid "
                    f"`{replacement_value}` (use a kebab-case ID)")

        for path, meta in metadata.items():
            spec_id = meta.get("id")
            status = meta.get("status")
            replacement_value = meta.get("superseded_by")
            replacement = (replacement_value
                           if isinstance(replacement_value, str) else None)
            supersedes = meta.get("supersedes")
            supersedes = supersedes if isinstance(supersedes, list) else []

            if status == "superseded" and not replacement:
                violations.append(
                    f"{path}:1: `superseded` spec missing `superseded_by`")
            if status in {"draft", "active"} and replacement:
                violations.append(
                    f"{path}:1: spec `{status}` cannot have `superseded_by`")
            if supersedes and status not in {"draft", "active"}:
                violations.append(
                    f"{path}:1: a spec that supersedes another must be draft or active")

            if replacement:
                replacement_path = ids.get(replacement)
                if replacement_path is None:
                    violations.append(
                        f"{path}:1: `superseded_by` references missing ID "
                        f"`{replacement}`")
                else:
                    replacement_meta = metadata[replacement_path]
                    if replacement_meta.get("status") not in {"draft", "active"}:
                        violations.append(
                            f"{path}:1: replacement `{replacement}` must be "
                            "draft or active")
                    if spec_id not in (replacement_meta.get("supersedes") or []):
                        violations.append(
                            f"{path}:1: non-reciprocal supersession with "
                            f"`{replacement}`")

            for old_id in supersedes:
                if not isinstance(old_id, str):
                    continue
                old_path = ids.get(old_id)
                if old_path is None:
                    violations.append(
                        f"{path}:1: `supersedes` references missing ID "
                        f"`{old_id}`")
                    continue
                old_meta = metadata[old_path]
                if old_meta.get("status") != "superseded":
                    violations.append(
                        f"{path}:1: superseded spec `{old_id}` must have status "
                        "superseded")
                if old_meta.get("superseded_by") != spec_id:
                    violations.append(
                        f"{path}:1: non-reciprocal supersession with `{old_id}`")

        direct = _linked_specs(root, specs_dir, index, documents)
        via_overview = set()
        for path in direct:
            if metadata[path].get("kind") == "overview":
                via_overview.update(
                    _linked_specs(root, specs_dir, path, documents))
        reachable = direct | via_overview
        for path, meta in metadata.items():
            if meta.get("status") in {"draft", "active"} and path not in reachable:
                violations.append(
                    f"{path}:1: spec `{meta.get('status')}` unreachable from "
                    "`specs/INDEX.md` directly or via an overview")


def lines_outside_fences(path):
    in_fence = False
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield n, line


def check_root_index(root, violations):
    index = root / "INDEX.md"
    if not index.is_file():
        return
    for n, line in lines_outside_fences(index):
        m = ROOT_ENTRY.match(line.strip())
        if m and len(m.group(1)) > MAX_ROOT_DESC:
            violations.append(f"{index}:{n}: description has {len(m.group(1))} "
                              f"characters (max. {MAX_ROOT_DESC})")


def note_limit(path):
    """Line limit for the file, or None when exempt.

    Planning artifacts have their own, shorter ruler: the plan root is the
    slice everyone reads and the front file is the slice one executor reads. A
    plan that does not fit **modularizes** into `subtasks/`; compressing it or
    splitting the task is the exception (see section 002 of the WORKFLOW).
    Judge Dredd's judgment and the historical artifacts of the retired
    adversarial gate follow the same logic, with the caps the
    [[specs/judge-dredd]] spec sets.
    """
    if path.name in EXEMPT_NAMES:
        return None
    if path.name.endswith(".excalidraw.md"):
        return None  # Excalidraw diagram: embedded JSON, not a note.
    for suffix, limit in GATE_ARTIFACT_LIMITS.items():
        if path.name.endswith(suffix):
            return limit
    if path.name.endswith(".plan.md"):
        return MAX_PLAN_LINES
    if path.parent.name == "subtasks":
        return MAX_FRONT_LINES
    return MAX_NOTE_LINES


def check_note_sizes(root, projects, violations):
    """Harness .md <=150 lines (plan: 80; front file in `subtasks/`: 50)."""
    for scope in projects:
        for path in poplib.iter_harness_markdown(scope):
            limit = note_limit(path)
            if limit is None:
                continue
            count = len(path.read_text(encoding="utf-8").splitlines())
            if count > limit:
                violations.append(f"{path}:1: {count} lines (max. {limit})")


def check_card_origin(card, meta, violations):
    """Origin frontmatter: roadmap requires epoch/phase; modifications
    requires `modification: M-<n>` (and does not require epoch/phase). An old
    card without `origin` is inferred from the id's `M-` prefix."""
    origin = meta.get("origin")
    if origin in (None, ""):
        origin = ("modifications"
                  if str(meta.get("id") or "").startswith("M-") else "roadmap")
    elif origin not in ORIGIN_VALUES:
        violations.append(f"{card}:1: `origin` invalid `{origin}` "
                          f"(use {' | '.join(ORIGIN_VALUES)})")
        return
    if origin == "roadmap":
        for field in ("epoch", "phase"):
            if meta.get(field) in (None, ""):
                violations.append(f"{card}:1: frontmatter missing `{field}` "
                                  "(roadmap origin)")
    elif not MODIFICATION_REF.fullmatch(str(meta.get("modification") or "")):
        violations.append(f"{card}:1: `modification` missing or invalid "
                          f"`{meta.get('modification')}` (use M-<n>)")


def check_cards(root, projects, violations):
    for project in projects:
        for stage, task_dir, card in poplib.iter_cards(project):
            meta = poplib.read_card(card)
            for field in CARD_REQUIRED:
                if meta.get(field) in (None, ""):
                    violations.append(f"{card}:1: frontmatter missing `{field}`")
            check_card_origin(card, meta, violations)
            if meta.get("stage") and meta["stage"] != stage:
                violations.append(f"{card}:1: stage `{meta['stage']}` differs "
                                  f"from folder `{stage}`")
            size = meta.get("size")
            if size not in (None, "") and str(size) not in SIZE_VALUES:
                violations.append(f"{card}:1: `size` invalid `{size}` "
                                  f"(use S | M | L)")
            kind = meta.get("return_kind")
            if kind not in (None, "") and str(kind) not in poplib.RETURN_KINDS:
                violations.append(
                    f"{card}:1: `return_kind` invalid `{kind}` "
                    f"(use {' | '.join(poplib.RETURN_KINDS)})")
            for gate in ("003", "005"):
                key = f"yolo_{gate}_returns"
                if key not in meta:
                    continue
                try:
                    count = int(meta[key])
                except (TypeError, ValueError):
                    count = -1
                if count < 0 or count > poplib.YOLO_RETURN_LIMIT:
                    violations.append(
                        f"{card}:1: `{key}` invalid `{meta[key]}` (use 0..2)")
            if meta.get("circuit_breaker") is True and meta.get("blocked") is not True:
                violations.append(
                    f"{card}:1: circuit breaker requires `blocked: true`")
            telemetry = poplib.telemetry_path(task_dir)
            if telemetry.is_file():
                data = poplib.read_telemetry(task_dir)
                if not data["events"] and telemetry.stat().st_size:
                    violations.append(f"{telemetry}: telemetry invalid")


def gate_pair_tolerated(meta):
    """Card older than the Judge Dredd cutoff — transition clause.

    A `created:` earlier than `JUDGE_DREDD_SINCE` means the task may have gone
    through the retired adversarial gate, so defense/accusation/judgment are
    tolerated history. It uses only an existing, immutable field; a missing or
    invalid `created:` grants no exemption (and is already a violation on its
    own).
    """
    created = _valid_iso_date(meta.get("created"))
    return created is not None and created.isoformat() < JUDGE_DREDD_SINCE


def gate_artifacts_of(task_dir):
    """This task's act-1 artifacts, as (path, family) pairs.

    It scans the folder instead of matching the literal name `<id><family>`,
    because the artifacts may be born per round (`<id>.r<n>.accusation.md`).
    What decides the family is the suffix; the round only tells the attempts
    apart.
    """
    found = []
    for path in sorted(task_dir.iterdir()):
        if not path.is_file():
            continue
        for family in (VERIFY_ARTIFACT, *RETIRED_GATE_ARTIFACTS):
            if not path.name.endswith(family):
                continue
            stem = path.name[: -len(family)]
            if ROUND_INFIX.sub("", stem) == task_dir.name:
                found.append((path, family))
            break
    return found


def check_gate_artifacts(root, projects, violations):
    """(k) artifacts of the retired adversarial gate in act 1 of 005_closing.

    Since `JUDGE_DREDD_SINCE`, act 1 is judged by the Judge Dredd, the single
    judge who writes `.verify.md` for every yolo task. `.defense.md`,
    `.accusation.md` and `.judgment.md` are no longer born: in a card created
    on or after the cutoff, any of them is a violation; in an older card they
    are tolerated history. The rule is per family, so it applies the same to
    every round (`<id>.r<n>.<artifact>.md`).

    **Absence is never a violation** — the rule is about the undue presence of
    a retired artifact, never a demand for the `.verify.md`.
    """
    for project in projects:
        for _, task_dir, card in poplib.iter_cards(project):
            meta = poplib.read_card(card)
            if gate_pair_tolerated(meta):
                continue
            for path, family in gate_artifacts_of(task_dir):
                if family in RETIRED_GATE_ARTIFACTS:
                    violations.append(
                        f"{path}:1: `{family}` retired — since "
                        f"{JUDGE_DREDD_SINCE} act 1 is the Judge Dredd, who "
                        f"writes `.verify.md`; a card created on or after the "
                        f"cutoff produces no adversarial-gate artifacts")


def check_verify_markers(root, projects, violations):
    """(l) Judge Dredd verdict markers in the `.verify.md`.

    A `.verify.md` that uses machine markers (`pop-verdict`/`pop-delta`, see
    [[specs/judge-dredd]]) must be coherent: **one judge per round**
    (a duplicated round is the re-judgment that blew the breaker in the
    field), **approval is terminal** (no verdict after `aprovada`) and
    **every return carries its own round's pop-delta**. A file without
    markers is tolerated legacy — demanding their presence is `pop_move`'s
    job, at return time; here only what exists is validated.
    """
    for project in projects:
        for _stage, task_dir, _card in poplib.iter_cards(project):
            verify = task_dir / f"{task_dir.name}{VERIFY_ARTIFACT}"
            if not verify.is_file():
                continue
            verdicts, deltas = poplib.parse_verify_markers(
                verify.read_text(encoding="utf-8"))
            seen, approved = set(), False
            for fields in verdicts:
                rnd = fields.get("round")
                decision = fields.get("decision")
                if approved:
                    violations.append(
                        f"{verify}:1: pop-verdict after `aprovada` — "
                        "approval is terminal; re-judgment does not exist")
                if decision not in poplib.VERDICT_DECISIONS:
                    violations.append(
                        f"{verify}:1: pop-verdict with invalid decision "
                        f"`{decision}` (use "
                        f"{' | '.join(poplib.VERDICT_DECISIONS)})")
                if rnd in seen:
                    violations.append(
                        f"{verify}:1: duplicated pop-verdict for round "
                        f"`{rnd}` — one judge per round")
                seen.add(rnd)
                if decision == "aprovada":
                    approved = True
                elif (decision in poplib.RETURN_KINDS
                        and rnd not in deltas):
                    violations.append(
                        f"{verify}:1: return `{decision}` without "
                        f"`pop-delta round={rnd}` — every return carries a "
                        "named delta")
            for rnd, fields in deltas.items():
                kind = fields.get("kind")
                if kind not in poplib.RETURN_KINDS:
                    violations.append(
                        f"{verify}:1: pop-delta round={rnd} with invalid "
                        f"kind `{kind}` (use "
                        f"{' | '.join(poplib.RETURN_KINDS)})")
                if fields.get("pontual") not in (None, "true", "false"):
                    violations.append(
                        f"{verify}:1: pop-delta round={rnd} with invalid "
                        f"pontual `{fields.get('pontual')}` (use true|false)")


def check_release(root, projects, warnings):
    for project in projects:
        for stage, task_dir, card in poplib.iter_cards(project):
            if stage != "001_initial_task" and not poplib.task_released(card):
                warnings.append(f"{card}:1: in {stage} without `- [x] Ready "
                                f"to plan` — was the release gate skipped?")


def check_worktrees(root, projects, warnings):
    for project in projects:
        harness = poplib.harness_root(project)
        wt_root = harness / "worktrees"
        if not wt_root.is_dir():
            continue
        for wt in sorted(p for p in wt_root.iterdir() if p.is_dir()):
            if not any(wt.iterdir()):
                continue
            if project == root and not TASK_DIR.match(wt.name):
                continue  # Rule 19 session worktree, not a task worktree.
            if not (harness / "kanban" / "004_processing" / wt.name).is_dir():
                warnings.append(f"{wt}: worktree without a matching task in "
                                f"004_processing")


MEMORY_TASK_ID = re.compile(
    r"^(?:\d+\.\d+\.\d+-[a-z0-9][a-z0-9-]*"
    r"|M-\d+\.\d+-[a-z0-9][a-z0-9-]*"
    r"|D-\d{8}-[a-z0-9][a-z0-9-]*"
    r"|F-\d{8}-[a-z0-9][a-z0-9-]*)$")


def _memory_entry_of(stem, ledger_stems):
    """(task, entry) if `stem` is an entry of a present ledger, else None.

    Matching against the ledgers that exist — instead of slicing the name by
    regex — is what resolves `8.1.10-foo`: the whole id matches as a ledger
    before any attempt to read `.10-foo` as an entry number.
    """
    for task in ledger_stems:
        if not stem.startswith(f"{task}."):
            continue
        match = MEMORY_ENTRY_SUFFIX.match(stem[len(task):])
        if match:
            return task, match.group(1)
    return None


def _check_memory_folder(folder, violations):
    """One date folder: one ledger per task and its subordinate entries."""
    files = [p for p in sorted(folder.iterdir()) if p.suffix == ".md"]
    for path in sorted(folder.iterdir()):
        if path.is_dir():
            violations.append(
                f"{path}: a memory date folder has no subfolder; ledger and "
                "entries sit side by side")
    ledgers = {p.stem: p for p in files if MEMORY_TASK_ID.match(p.stem)}
    ledger_text = {}
    for task, path in sorted(ledgers.items()):
        text = path.read_text(encoding="utf-8")
        ledger_text[task] = text
        meta, _ = poplib.parse_frontmatter(text)
        if meta.get("task") != task:
            violations.append(
                f"{path}:1: `task` `{meta.get('task')}` differs from the file "
                f"name `{task}`")
        for field in pop_roadmap.REQUIRED_MEMORY:
            if meta.get(field) in (None, ""):
                violations.append(f"{path}:1: ledger without `{field}`")
        if str(meta.get("finished") or "") != folder.name:
            violations.append(
                f"{path}:1: `finished` `{meta.get('finished')}` differs from "
                f"the folder `{folder.name}`; the folder is the completion date")
        if len(text) > MAX_MEMORY_LEDGER:
            violations.append(
                f"{path}:1: ledger with {len(text)} characters "
                f"(max. {MAX_MEMORY_LEDGER}) — move content into entries")

    for path in files:
        if path.stem in ledgers:
            continue
        parsed = _memory_entry_of(path.stem, ledgers)
        if parsed is None:
            violations.append(
                f"{path}:1: name outside the memory layout; use `<id>.md` "
                "(ledger) or `<id>.<nn>-<slug>.md` (entry) with the ledger in "
                "the same folder")
            continue
        task, entry = parsed
        text = path.read_text(encoding="utf-8")
        meta, _ = poplib.parse_frontmatter(text)
        if meta.get("task") != task:
            violations.append(
                f"{path}:1: `task` `{meta.get('task')}` differs from the "
                f"ledger `{task}`")
        if meta.get("entry") != entry:
            violations.append(
                f"{path}:1: `entry` `{meta.get('entry')}` differs from the "
                f"file name `{entry}`")
        if len(text) > MAX_MEMORY_ENTRY:
            violations.append(
                f"{path}:1: entry with {len(text)} characters "
                f"(max. {MAX_MEMORY_ENTRY}) — it is almost always two entries")
        if not WIKILINK.search(text):
            violations.append(
                f"{path}:1: entry without an evidence wikilink; point at the "
                "spec or the file that attests the change")
        if f"[[{path.stem}" not in ledger_text.get(task, ""):
            violations.append(
                f"{path}:1: orphaned entry — not indexed under `## Entries` of "
                f"the ledger `{task}.md`")


def check_memory(root, projects, violations):
    """(m) `memory/` in the granular layout: date folder, ledger and entries.

    Flat memory in `memory/<id>.md` is tolerated legacy while `finished` is
    earlier than `MEMORY_LAYOUT_SINCE`, and the layout requirement only reaches
    the **current scope** (`scope == root`). A nested scope validates its own
    memory when it runs its own `pop_validate`: demanding the layout of an
    `uni-repo` clone here would be telling this vault to rewrite memory that is
    not its own — and the ruler would be born failing work in flight in there.
    The content of the date folders, when they exist, is validated in any scope:
    there the layout has already been adopted and what is checked is coherence,
    not migration.
    """
    for scope in projects:
        base = poplib.harness_root(scope) / "memory"
        if not base.is_dir():
            continue
        for child in sorted(base.iterdir()):
            if child.is_dir():
                if _valid_iso_date(child.name) is None:
                    violations.append(
                        f"{child}: a `memory/` folder must be a "
                        "`YYYY-MM-DD` date (the task's completion date)")
                    continue
                _check_memory_folder(child, violations)
            elif child.suffix == ".md" and scope == root:
                meta, _ = poplib.parse_frontmatter(
                    child.read_text(encoding="utf-8"))
                if str(meta.get("finished") or "") >= MEMORY_LAYOUT_SINCE:
                    violations.append(
                        f"{child}:1: memory loose in `memory/`; since "
                        f"{MEMORY_LAYOUT_SINCE} the ledger lives in "
                        "`memory/<YYYY-MM-DD>/<id>.md`")


def check_roadmap_residuals(root, violations):
    """A completed task with memory cannot remain in the roadmap or the
    modifications (in MODIFICATIONS.md the leftover is the task wikilink)."""
    for scope, path, number, task_id in pop_roadmap.residuals(root):
        memory = pop_roadmap.memory_path(root, scope, task_id)
        # Ignore untracked external clones so validation never mutates their scope.
        if scope != root and not pop_roadmap.tracked(root, memory):
            continue
        violations.append(
            f"{path}:{number}: residual completed task `{task_id}` — "
            "remove the row (or the wikilink, in MODIFICATIONS.md) after "
            "validating memory")


# Legacy harness markers are rejected by the positive anatomy whitelist.
LEGACY_MARKERS = ("kanban", ".unirepo-harness.json")


def _scan_legacy_markers(scope, root, violations):
    for name in LEGACY_MARKERS:
        if (scope / name).exists():
            violations.append(
                f"{(scope / name)}: harness outside `pop/` — legacy anatomy / "
                f"rule boundary 13; move the harness to `pop/`")


def check_strict_anatomy(root, violations):
    projects = root / "projects"
    if not projects.is_dir():
        return
    for project in sorted(projects.glob("*")):
        if not project.is_dir():
            continue
        if any(part.startswith(".") for part in project.relative_to(root).parts):
            continue
        _scan_legacy_markers(project, root, violations)
        # one more level: multi-repo repository
        for sub in sorted(project.glob("*")):
            if sub.is_dir() and sub.name != "pop" and not sub.name.startswith("."):
                _scan_legacy_markers(sub, root, violations)


def _stage_artifact_base(stem):
    """The task id behind a stage-artifact stem.

    It strips the artifact suffix and, behind it, the round infix — `<id>`,
    `<id>.verify` and `<id>.r2.accusation` all reduce to the same `<id>`.
    """
    for suffix in STAGE_ARTIFACT_SUFFIXES:
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
            break
    return ROUND_INFIX.sub("", stem)


def _is_stage_artifact_of(name, base):
    """`name` is a stage artifact of task `base`, with or without a round."""
    return (any(name.endswith(suffix) for suffix in STAGE_ARTIFACT_SUFFIXES)
            and _stage_artifact_base(name) == base)


def check_wikilinks(root, warnings):
    targets = set()
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if LINK_SKIP_PARTS & set(rel.parts):
            continue
        rel = rel.as_posix().lower()
        targets.update({path.name.lower(), path.stem.lower(), rel})
        if rel.endswith(".md"):
            targets.add(rel[:-3])
    for path in sorted(poplib.iter_all_harness_markdown(root)):
        if path.name.endswith(".excalidraw.md"):
            continue
        for n, line in lines_outside_fences(path):
            for m in WIKILINK.finditer(INLINE_CODE.sub("", line)):
                # A trailing backslash escapes a pipe in table aliases (`[[x\|y]]`).
                target = m.group(1).strip().rstrip("\\")
                if not target or "<" in target or set(target) <= {"."}:
                    continue
                low = target.lower()
                name = low.rsplit("/", 1)[-1]
                if {low, f"{low}.md", name} & targets:
                    continue
                src_task = _stage_artifact_base(path.stem.lower())
                if _is_stage_artifact_of(name, src_task):
                    continue
                warnings.append(f"{path}:{n}: broken wikilink [[{target}]]")


def check_hash_pins(root, violations):
    for path in sorted(root.rglob("*.md")):
        parts = set(path.relative_to(root).parts)
        if parts & LINK_SKIP_PARTS or "_templates" in parts or "raw" in parts:
            continue
        for n, line in lines_outside_fences(path):
            for m in POP_HASH.finditer(line):
                relpath, digest = m.group(1), m.group(2).lower()
                if len(digest) != 64:
                    violations.append(f"{path}:{n}: malformed pop-hash "
                                      f"(sha256 has {len(digest)} hex digits, "
                                      f"expected 64)")
                    continue
                target = (path.parent / relpath).resolve()
                if not target.is_file():
                    violations.append(f"{path}:{n}: pop-hash cites missing file "
                                      f"`{relpath}`")
                    continue
                actual = hashlib.sha256(target.read_bytes()).hexdigest()
                if actual != digest:
                    violations.append(
                        f"{path}:{n}: pop-hash mismatch for `{relpath}` — "
                        f"the cited file changed; review the citation and "
                        f"update to sha256={actual}")


def _dox_block_lines(lines):
    """Lines of the DOX block, from the heading carrying the marker up to the
    next heading of equal or higher level (or the end of the file).

    An application embeds the DOX process in its AGENTS.md and only for that
    reason exceeds the cap (rule 5). Delimiting the block is what allows
    **discounting** it instead of switching the ruler off: without this,
    "exempt" became "not measured", and the file grew with nobody complaining —
    that is how an application's AGENTS.md reached 162 lines of text that was
    not DOX.
    """
    start = next((n for n, line in enumerate(lines)
                  if line.lstrip().startswith("#") and DOX_MARKER in line), None)
    if start is None:
        return 0
    level = len(lines[start]) - len(lines[start].lstrip("#"))
    for n in range(start + 1, len(lines)):
        line = lines[n]
        if not line.startswith("#"):
            continue
        if len(line) - len(line.lstrip("#")) <= level:
            return n - start
    return len(lines) - start


def check_project_agents(root, projects, violations, warnings):
    """A project's AGENTS.md fits in 60 lines — it is a pointer, not a copy.

    The file grows on its own whenever it narrates the flow instead of linking
    the WORKFLOW, and the narration rots at the first stage change. **The ruler
    always measures**: in an application the DOX block is discounted (rule 5)
    and the remaining excess comes out as a **warning**, not a violation — the
    debt belongs to whoever hosts the file and is paid in their scope, but it
    must not be invisible. Outside an application, the cap stays a violation.
    The root AGENTS.md is the vault's, not a project's: out of reach.
    """
    for project in projects:
        if project == root:
            continue
        path = project / "AGENTS.md"
        if not path.is_file():
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        dox = _dox_block_lines(lines)
        total = len(lines) - dox
        if total <= MAX_PROJECT_AGENTS:
            continue
        message = (f"{path}:1: {total} lines (max. {MAX_PROJECT_AGENTS}"
                   f"{f', DOX block of {dox} already discounted' if dox else ''})"
                   " — point at the WORKFLOW instead of narrating the flow")
        (warnings if dox else violations).append(message)


def check_harness_freshness(root, projects, violations):
    """A harness installed in a project is at the source's version.

    The root PoP is the single source: a project with
    `pop/.unirepo-harness.json` received a managed copy of the WORKFLOW, the
    templates and the scripts. If the `content_sha` stamp diverges, that
    project is running a flow the vault has already abandoned — fail closed,
    because the remedy is a single command. Only the vault that **is** the
    source runs this check (a clone does not audit itself).
    """
    try:
        import pop_install_unirepo as installer
    except ImportError:
        return
    if installer.SOURCE != root or not installer.MANIFEST.is_file():
        return
    current = installer.content_sha()
    for project in projects:
        marker, stamped = installer.installed_stamp(project)
        if marker is None:
            continue
        label = project.relative_to(root)
        if stamped is None:
            violations.append(
                f"{marker}: harness without a `content_sha` stamp — reinstall "
                f"with `python3 scripts/pop_install_unirepo.py {label}`")
        elif stamped != current:
            violations.append(
                f"{marker}: harness STALE ({stamped[:12]} ≠ source "
                f"{current[:12]}) — reinstall with "
                f"`python3 scripts/pop_install_unirepo.py {label}`")


def check_standalone(root, violations):
    hb = root / "pop"
    manifest_path = hb / ".unirepo-harness.json"
    if not manifest_path.is_file():
        violations.append(f"{manifest_path}: standalone manifest missing")
        return
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        violations.append(f"{manifest_path}: JSON invalid: {error}")
        return
    for name in data.get("files", []):
        if not (hb / name).is_file():
            violations.append(f"{hb / name}: required file missing")
    for name in data.get("directories", []):
        if not (hb / name).is_dir():
            violations.append(f"{hb / name}: required directory missing")
    for name in data.get("skills", []):
        path = root / ".agents/skills" / name / "SKILL.md"
        if not path.is_file():
            violations.append(f"{path}: required skill missing")
    for name in data.get("anatomy", []):
        if not (hb / name).is_dir():
            violations.append(f"{hb / name}: required anatomy directory missing")
    for name in data.get("keep_files", []):
        if not (hb / name).is_file():
            violations.append(f"{hb / name}: required Git marker missing")
    for path in root.rglob("*.md"):
        parts = set(path.relative_to(root).parts)
        if parts & {".git", "worktrees", "kanban"}:
            continue
        for n, line in lines_outside_fences(path):
            if EXTERNAL_PROJECT_LINK.search(line):
                violations.append(
                    f"{path}:{n}: link points outside the scope")


def main():
    parser = argparse.ArgumentParser(
        description="Validate vault limits: 144 characters, 150 lines, "
                    "card frontmatter, orphaned worktrees, broken wikilinks, "
                    "adopted specs, and pop-hash code citations.")
    parser.add_argument("--scope", "--vault", dest="vault", metavar="DIR",
                        help="vault root (default: directory above scripts/)")
    parser.add_argument("--standalone", action="store_true",
                        help="fail closed for the local uni-repo contract")
    args = parser.parse_args()

    root = poplib.vault_root(args.vault)
    projects = poplib.discover_projects(root)

    violations, warnings = [], []
    check_root_index(root, violations)
    check_note_sizes(root, projects, violations)
    check_cards(root, projects, violations)
    check_gate_artifacts(root, projects, violations)
    check_verify_markers(root, projects, violations)
    check_release(root, projects, warnings)
    check_worktrees(root, projects, warnings)
    check_memory(root, projects, violations)
    check_roadmap_residuals(root, violations)
    check_strict_anatomy(root, violations)
    check_spec_collections(root, projects, violations)
    check_wikilinks(root, warnings)
    check_hash_pins(root, violations)
    check_project_agents(root, projects, violations, warnings)
    check_harness_freshness(root, projects, violations)
    if args.standalone:
        check_standalone(root, violations)

    for w in warnings:
        print(f"[WARNING] {w}")
    for v in violations:
        print(f"[VIOLATION] {v}")
    if violations:
        print(f"\n{len(violations)} violation(s) found.")
        return 1
    if args.standalone:
        print("standalone valid")
    print("Vault valid — no violations found."
          + (f" ({len(warnings)} warning(s).)" if warnings else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
