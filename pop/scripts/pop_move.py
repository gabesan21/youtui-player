#!/usr/bin/env python3

import argparse
import shutil
import subprocess
import sys

import poplib

RETURNS = {
    ("003_human_approval", "002_planning"),
    ("004_processing", "002_planning"),
    ("005_closing", "004_processing"),
    ("005_closing", "002_planning"),
}

# Returns that fail the plan, not the execution (`yolo_003_returns` counter).
PLAN_RETURNS = {
    ("003_human_approval", "002_planning"),
    ("005_closing", "002_planning"),
}


def transition_allowed(src, dst, *, yolo_single_gate=False):
    """True when dst is src's next stage or a permitted return.

    `yolo_single_gate` (non-critical yolo task) allows the 002→004 jump:
    yolo's single quality gate is the one in 005_closing (see the WORKFLOW's
    Yolo mode section).
    """
    stages = poplib.STAGES
    if stages.index(dst) == stages.index(src) + 1:
        return True
    if yolo_single_gate and (src, dst) == ("002_planning", "004_processing"):
        return True
    return (src, dst) in RETURNS


def resolve_return_kind(src, dst, requested):
    """Classification to write in `return_kind:`, or (None, error message).

    A return is incremental, so the kind is required wherever it changes what
    happens next: `005_closing→002` decides between amending the plan
    (`lacuna`) and replanning (`premissa`), and that choice also sets the mode
    of the re-review. `005_closing→004` is always `execucao`. In every other
    transition the field does not apply — in `003→002` nothing has been
    executed yet.
    """
    if (src, dst) == ("005_closing", "002_planning"):
        if requested in ("lacuna", "premissa"):
            return requested, None
        return None, ("CLASSIFY THE RETURN: a plan defect requires "
                      "`--return-kind lacuna` (incomplete plan, what was "
                      "delivered is correct → amendment) or `--return-kind "
                      "premissa` (wrong strategy → replanning). Without it "
                      "002 does not know the size of the fix (use --force for "
                      "exceptions).")
    if (src, dst) == ("005_closing", "004_processing"):
        if requested in (None, "execucao"):
            return "execucao", None
        return None, (f"INCOMPATIBLE RETURN: `{requested}` classifies a plan "
                      "defect and goes to 002_planning; the route to 004 is "
                      "always `execucao` (use --force for exceptions).")
    if requested:
        return None, (f"`--return-kind` does not apply to {src} → {dst}: only "
                      "returns leaving 005_closing are classified (use "
                      "--force for exceptions).")
    return None, None


def git_head(project):
    """HEAD of the repo containing the project, or None without git."""
    try:
        out = subprocess.run(["git", "-C", str(project), "rev-parse", "HEAD"],
                             capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.stdout.strip() or None


def git_changed_paths(project, base):
    """Files changed since `base` (worktree included), or None without git."""
    try:
        out = subprocess.run(
            ["git", "-C", str(project), "diff", "--name-only", base],
            capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return [line.strip() for line in out.stdout.splitlines() if line.strip()]


def verify_gate_error(task_dir, task_id, dst, return_kind):
    """Refusal of a 005→004/002 return based on the `.verify.md` markers.

    The round's verdict is the gate's executable contract: without it the
    return is the orchestrator's guess. The locks cut off the bugs observed
    in the field: re-judging an approval, the full route for a pinpoint delta
    and a return without a delta.
    """
    verify = task_dir / f"{task_id}.verify.md"
    if not verify.is_file():
        return ("NO JUDGMENT: a return leaving 005_closing requires "
                f"`{verify.name}` with the round's verdict — a judge that "
                "rejects without an artifact does not return (use --force "
                "for exceptions).")
    verdicts, deltas = poplib.parse_verify_markers(
        verify.read_text(encoding="utf-8"))
    if not verdicts:
        return ("NO VERDICT MARKER: end the round in the "
                f"`{verify.name}` with `<!-- pop-verdict round=<n> "
                "decision=... -->` (and `<!-- pop-delta ... -->` when "
                "returning) before moving (use --force for exceptions).")
    last = verdicts[-1]
    decision = last.get("decision")
    if decision == "aprovada":
        return ("APPROVAL IS TERMINAL: the last pop-verdict in the "
                f"`{verify.name}` approves the task — there is no "
                "re-judgment nor independent review over an approval; "
                "proceed to delivery/close-out (use --force for exceptions).")
    if decision == "reparo-dirigido":
        return ("DIRECTED REPAIR IN PROGRESS: a pinpoint delta does not "
                "become a route — dispatch the patch and collect the "
                "judge's addendum; only an addendum that returns authorizes "
                "moving (use --force for exceptions).")
    expected = "execucao" if dst == "004_processing" else return_kind
    if decision != expected:
        return (f"INCOMPATIBLE VERDICT: the last pop-verdict declares "
                f"`{decision}`, but the requested route is `{expected}` — "
                "route and verdict go together (use --force for exceptions).")
    delta = deltas.get(last.get("round"))
    if not delta:
        return ("RETURN WITHOUT DELTA: the verdict returns but the "
                f"`<!-- pop-delta round={last.get('round')} ... -->` is "
                f"missing from the `{verify.name}` — without a delta, 002 "
                "does not know whether to amend or replan and 004 does not "
                "know what to re-execute (use --force for exceptions).")
    if decision == "execucao" and delta.get("pontual") == "true":
        return ("PINPOINT DELTA: a `pontual=true` blocker follows the "
                "default directed-repair route (no pop_move, no counter); "
                "the full route is for a diffuse defect — with the round's "
                "2 repairs exhausted, repeat with --force and the reason in "
                "--reason.")
    return None


def reentry_gate_error(project, task_dir, task_id, meta):
    """Refusal of a 004→005 reentry with no work on the delta's paths.

    It only acts when the evidence is complete (a delta with `paths`,
    `return_base` and git available) — fail-open otherwise: the lock exists
    to cut off re-presenting the same problem to the judge, not to block
    legacy flow.
    """
    base = str(meta.get("return_base") or "").strip()
    if not base or meta.get("return_kind") not in poplib.RETURN_KINDS:
        return None
    verify = task_dir / f"{task_id}.verify.md"
    if not verify.is_file():
        return None
    _verdicts, deltas = poplib.parse_verify_markers(
        verify.read_text(encoding="utf-8"))
    if not deltas:
        return None
    last_delta = list(deltas.values())[-1]
    paths = poplib.marker_paths(last_delta)
    if not paths:
        return None
    changed = git_changed_paths(project, base)
    if changed is None:
        return None
    for path in paths:
        for touched in changed:
            if (touched == path or touched.endswith("/" + path)
                    or path.endswith("/" + touched)):
                return None
    return ("REENTRY WITHOUT WORK ON THE DELTA: no delta path "
            f"({', '.join(paths)}) changed since `return_base` {base[:12]} — "
            "re-presenting the same problem to the judge burns a round for "
            "nothing; execute the delta before moving (use --force for "
            "exceptions).")


def update_card(card, new_stage, reason, fields=None):
    lines = card.read_text(encoding="utf-8").splitlines()
    date = poplib.today()
    fields = fields or {}
    found = set()
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                end = i
                break
            key = lines[i].split(":", 1)[0].strip()
            if key == "stage":
                lines[i] = f"stage: {new_stage}"
            elif key == "updated":
                lines[i] = f"updated: {date}"
            elif key in fields:
                lines[i] = f"{key}: {fields[key]}"
                found.add(key)
        for key, value in fields.items():
            if key not in found:
                lines.insert(end, f"{key}: {value}")
    card.write_text(append_log(lines, f"- {date} — {reason}") + "\n",
                    encoding="utf-8")


def append_log(lines, entry):
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == "## Log")
    except StopIteration:
        return "\n".join(lines).rstrip("\n") + f"\n\n## Log\n\n{entry}"
    end = next((j for j in range(start + 1, len(lines))
                if lines[j].startswith("## ")), len(lines))
    last = end - 1
    while last > start and not lines[last].strip():
        last -= 1
    lines.insert(last + 1, entry)
    return "\n".join(lines).rstrip("\n")


def main():
    parser = argparse.ArgumentParser(
        description="Move a task folder to another kanban stage and update "
                    "the card frontmatter and log.")
    parser.add_argument("task_id", help="task ID (folder name, for example "
                                        "1.1.1-user-table-creation)")
    parser.add_argument("stage", choices=poplib.STAGES,
                        help="destination stage")
    parser.add_argument("--reason", default="transition via pop_move",
                        help="short reason recorded in the card log")
    parser.add_argument("--return-kind", choices=poplib.RETURN_KINDS,
                        help="classification of a return leaving 005_closing: "
                             "lacuna|premissa (→002, required) or execucao "
                             "(→004, default)")
    parser.add_argument("--context", action="append", default=[],
                        help="agent context used at this stage; repeatable")
    parser.add_argument("--test-seconds", type=float, default=0,
                        help="test time associated with this transition")
    parser.add_argument("--by", default=poplib.default_agent(),
                        help="agent identifier (default: user@host; same as pop_claim)")
    parser.add_argument("--force", action="store_true",
                        help="allow a nonstandard transition and override claim/release")
    parser.add_argument("--scope", "--vault", dest="vault", metavar="DIR",
                        help="vault root (default: directory above scripts/)")
    args = parser.parse_args()

    root = poplib.vault_root(args.vault)
    found = poplib.find_task(root, args.task_id)
    if not found:
        print(f"Task not found in any project: {args.task_id}")
        return 1
    project, src, task_dir = found
    label = poplib.project_label(root, project)
    if src == args.stage:
        print(f"Task {args.task_id} is already in {src} ({label}).")
        return 1
    card_src = task_dir / f"{args.task_id}.md"
    meta = poplib.read_card(card_src) if card_src.is_file() else {}
    yolo_single_gate = (meta.get("yolo") is True
                        and meta.get("critical") is not True)
    if (not transition_allowed(src, args.stage,
                               yolo_single_gate=yolo_single_gate)
            and not args.force):
        print(f"Transition not allowed: {src} → {args.stage}. "
              f"Flow: 001→002→003→004→005_closing (non-critical yolo: "
              f"002→004 directly, no 003); returns: 003→002, 004→002, "
              f"005_closing→004 (execution) and 005_closing→002 (plan "
              f"defect). Use --force for exceptions.")
        return 1

    if card_src.is_file() and not args.force:
        by, at = poplib.parse_claim(meta)
        if by and by != args.by and not poplib.claim_expired(at):
            print(f"CLAIMED: {args.task_id} has an active claim by {by} since "
                  f"{at.isoformat(timespec='minutes')} — do not move another "
                  f"agent's task (use --force for exceptions).")
            return 1
        if (src == "001_initial_task" and args.stage == "002_planning"
                and meta.get("yolo") is not True
                and not poplib.task_released(card_src)):
            print(f"NOT RELEASED: {args.task_id} does not yet have "
                  f"`- [x] Ready to plan` in the card's Release section — "
                  f"the human releases stage 001 (use --force for exceptions).")
            return 1

    return_gate = None
    if (src, args.stage) in PLAN_RETURNS:
        return_gate = "003"
    elif (src, args.stage) == ("005_closing", "004_processing"):
        return_gate = "005"

    return_kind, kind_error = resolve_return_kind(src, args.stage,
                                                  args.return_kind)
    if kind_error and not args.force:
        print(kind_error)
        return 1

    if meta.get("yolo") is True and not args.force:
        if src == "005_closing" and args.stage in ("004_processing",
                                                   "002_planning"):
            gate_error = verify_gate_error(task_dir, args.task_id,
                                           args.stage, return_kind)
            if gate_error:
                print(gate_error)
                return 1
        if (src, args.stage) == ("004_processing", "005_closing"):
            gate_error = reentry_gate_error(project, task_dir,
                                            args.task_id, meta)
            if gate_error:
                print(gate_error)
                return 1

    fields = {}
    if return_kind:
        fields["return_kind"] = return_kind
        if src == "005_closing":
            head = git_head(project)
            if head:
                fields["return_base"] = head
    if meta.get("yolo") is True and return_gate:
        key = f"yolo_{return_gate}_returns"
        try:
            attempts = int(meta.get(key) or 0)
        except (TypeError, ValueError):
            attempts = 0
        if attempts >= poplib.YOLO_RETURN_LIMIT and not args.force:
            reason = (f"yolo circuit breaker at {return_gate}: the third "
                      "failure requires human diagnosis")
            update_card(card_src, src, reason, {
                "blocked": "true", "blocked_reason": reason,
                "circuit_breaker": "true"})
            poplib.record_telemetry(task_dir, {
                "event": "circuit_breaker", "stage": src,
                "gate": return_gate, "contexts": args.context,
                "test_seconds": args.test_seconds, "result": "blocked"})
            print(f"BLOCKED: {args.task_id} — {reason}.")
            return 1
        fields[key] = attempts + 1

    dest_dir = poplib.harness_root(project) / "kanban" / args.stage
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / args.task_id
    if dest.exists():
        print(f"Destination already exists: {dest}")
        return 1
    shutil.move(str(task_dir), str(dest))

    card = dest / f"{args.task_id}.md"
    if card.is_file():
        update_card(card, args.stage, f"{src}→{args.stage} — {args.reason}", fields)
        poplib.record_telemetry(dest, {
            "event": "transition", "from": src, "to": args.stage,
            "contexts": args.context, "test_seconds": args.test_seconds,
            "return_kind": return_kind,
            "result": "returned" if return_gate else "advanced"})
    else:
        print(f"[WARNING] card not found for update: {card}")
    print(f"OK: {args.task_id} ({label}) moved {src} → {args.stage}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
