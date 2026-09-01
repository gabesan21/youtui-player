#!/usr/bin/env python3
"""pop_task — scaffolding for a new task in 001_initial_task.

Creates `kanban/001_initial_task/<id>/<id>.md` in the indicated project's
harness (`pop/kanban/...` in the new anatomy, `kanban/...` in the legacy one)
from `_templates/TASK.md`, filling in id, project, origin (roadmap epoch/phase
or modification), dates and title, and creates an empty `subtasks/` folder.
Refuses if the task already exists in any project/stage (ids are unique
across the vault).

Two id origins: roadmap `<epoch>.<phase>.<task>-<slug>` (e.g.
1.2.3-user-table) and modifications `M-<modification>.<task>-<slug>` (e.g.
M-1.1-adjust-contract — task 1 of modification M-1).

Usage:
    python3 scripts/pop_task.py <project> <task-id> [--title "..."]
    e.g.: python3 scripts/pop_task.py my-project 1.2.3-user-table-creation
          python3 scripts/pop_task.py my-project M-1.1-adjust-contract
    Multi-repo repository: <project>/<repo>.
"""

import argparse
import re
import sys

import poplib

ROADMAP_ID = re.compile(r"^(\d+)\.(\d+)\.(\d+)-([a-z0-9][a-z0-9-]*)$")
MODIFICATION_ID = re.compile(r"^M-(\d+)\.(\d+)-([a-z0-9][a-z0-9-]*)$")


def fill_template(template, task_id, project, title):
    """Replaces the obvious placeholders of _templates/TASK.md.

    Fills only the frontmatter block of the task's origin and deletes the
    unused one, as the template instructs: roadmap keeps `epoch`/`phase`
    (no `modification`); modifications keeps `modification: M-<n>`
    (no `epoch`/`phase`).
    """
    date = poplib.today()
    roadmap = ROADMAP_ID.match(task_id)
    text = template
    if roadmap:
        epoch, phase_n, task_n, slug = roadmap.groups()
        numeric_id = f"{epoch}.{phase_n}.{task_n}"
        text = text.replace("\nmodification:\n", "\n")
        pairs = [
            ("<n>.<m>.<t>", numeric_id),
            ("<n>.<m>", f"{epoch}.{phase_n}"),
            ("<n>", epoch),
        ]
    else:
        mod_n, task_n, slug = MODIFICATION_ID.match(task_id).groups()
        numeric_id = f"M-{mod_n}.{task_n}"
        text = text.replace("\nepoch: <n>\n", "\n")
        text = text.replace('\nphase: "<n>.<m>"\n', "\n")
        text = text.replace("\nmodification:\n", f"\nmodification: M-{mod_n}\n")
        pairs = [
            ("<n>.<m>.<t>", numeric_id),
            ("origin: roadmap", "origin: modifications"),
            ("M-<n>", f"M-{mod_n}"),
        ]
    pairs += [
        ("<project>", project),
        ("<id>-<slug>", task_id),
        ("<short title>", title or slug.replace("-", " ")),
        ("created: YYYY-MM-DD", f"created: {date}"),
        ("updated: YYYY-MM-DD", f"updated: {date}"),
        ("- YYYY-MM-DD — created in 001_initial_task — <reason/origin>",
         f"- {date} — created in 001_initial_task — via pop_task"),
    ]
    for old, new in pairs:
        text = text.replace(old, new)
    return text


def main():
    parser = argparse.ArgumentParser(
        description="Creates the folder and card of a new task in "
                    "kanban/001_initial_task, from _templates/TASK.md.")
    parser.add_argument("project", metavar="PROJECT",
                        help="destination project (e.g. my-project; "
                             "multi-repo repository: my-app/frontend)")
    parser.add_argument("task_id", metavar="TASK-ID",
                        help="full task id (e.g. 1.2.3-user-table-creation "
                             "or M-1.1-adjust-contract)")
    parser.add_argument("--title", help="short card title "
                                        "(default: slug with spaces)")
    parser.add_argument("--scope", "--vault", dest="vault", metavar="DIR",
                        help="vault root (default: folder above scripts/)")
    args = parser.parse_args()

    modification = MODIFICATION_ID.match(args.task_id)
    if not modification and not ROADMAP_ID.match(args.task_id):
        print(f"Invalid id: {args.task_id} — expected "
              f"<epoch>.<phase>.<task>-<kebab-slug> (e.g. 1.2.3-user-table) or "
              f"M-<modification>.<task>-<kebab-slug> (e.g. M-1.1-adjust-contract).")
        return 1

    root = poplib.vault_root(args.vault)
    project_dir = poplib.project_dir(root, args.project)
    harness = poplib.harness_root(project_dir)  # pop/ in the new anatomy
    if not (harness / "kanban").is_dir():
        print(f"Project without kanban/ (nor pop/kanban/): {project_dir} — "
              f"check <project>[/<repo>].")
        return 1
    existing = poplib.find_task(root, args.task_id)
    if existing:
        _, stage, task_dir = existing
        print(f"Task already exists in {stage}: {task_dir}")
        return 1
    template_path = poplib.templates_dir(root) / "TASK.md"
    if not template_path.is_file():
        print(f"Template not found: {template_path}")
        return 1

    task_dir = harness / "kanban" / "001_initial_task" / args.task_id
    task_dir.mkdir(parents=True)
    (task_dir / "subtasks").mkdir()
    card = task_dir / f"{args.task_id}.md"
    card.write_text(
        fill_template(template_path.read_text(encoding="utf-8"),
                      args.task_id, args.project, args.title),
        encoding="utf-8")
    print(f"OK: task created at {card}")
    if modification:
        print("Reminder: fill in 'What', 'Why' and depends_on, and link "
              "[[{}]] in the modification (MODIFICATIONS.md or "
              "modifications/m-{}-*.md).".format(args.task_id,
                                                 modification.group(1)))
    else:
        print("Reminder: fill in 'What', 'Why' and depends_on, and link "
              "[[{}]] in the epoch file.".format(args.task_id))
    print("The task only leaves 001 once the human checks "
          "`- [x] Ready to plan` (Release section of the card).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
