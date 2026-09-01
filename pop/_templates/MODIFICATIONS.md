# Modifications — <Project name>

> Blockquotes in this template are fill-in instructions — **delete them when filling it in**.

Profile: [[pop/PROJECT|<Project name>]] · Roadmap: [[pop/ROADMAP|Roadmap]]

> Tracking of whatever arrives **outside the plan**: hotfixes, one-off tweaks, contract fixes/changes and small emergent features. One line per modification, always a short description; `M-<n>.<t>-<slug>` tasks live in the modification's file in `pop/modifications/` when multi-task ([[_templates/MODIFICATION|template]]; a scope whose harness lives at its own root: without the `pop/` prefix). Never add detail here.
> **Before anything, the rule-13 triage of [[AGENTS|AGENTS]]:** a pinpoint fix does not even become a modification — it runs as a direct fix and lives only in memory + specs ("Direct fix" section of [[WORKFLOW|WORKFLOW]]).
> **Frontier with the roadmap (3 questions):** does it fit in ~3 tasks? Does the what/how fit in a card, without a planning interview? Does it only touch existing contracts? Any "no" → roadmap via `plan-roadmap`. When in doubt, modification. **Only the human creates a modification** (the agent proposes); the `weekly-review` proposes promotion to the roadmap when one swells.
> **Yolo:** only the human marks it — append ` · yolo: yes` to the end of the Description cell; tasks inherit, with per-task opt-out/opt-in. **Size:** the agent suggests `S|M|L` in the Description.
> **This file is a kanban, not a history:** a completed modification's row is **removed** by the `weekly-review` — no log remains; the durable record is memory + specs. **Task** rows leave the modification files after valid memory (rule 17 of [[AGENTS|AGENTS]]). `M-<n>` ids are never reused — check memory and the kanban before proposing the next one.

| # | Modification | Description (≤1 line) | Status |
|---|--------------|-----------------------|--------|
| M-1 | [[pop/modifications/m-1-<slug>\|<name>]] (multi-task) or loose name (single task) | What changes and why. · size: S | open |

**Modification status:** open | in progress | completed
