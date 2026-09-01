---
name: new-task
description: Quick interview that creates a task from the roadmap or a modification as a folder in pop/kanban/001_initial_task, with the card filled in, specs linked and a link in the epoch/modification. Use when the user asks to start/create a task or requests a change with no active card.
---

# new-task

Materializes a roadmap or modification task as a folder in the kanban, at stage `001_initial_task` — **confirming the essentials with the user before creating**. Full flow: [[WORKFLOW|WORKFLOW]].

**Yolo mode (no interview):** a yolo-scope task (Yolo mode section of the WORKFLOW) is materialized directly by the orchestrator — the answers come from the roadmap/modifications (task description, dependencies from the table, `critical` from the project's default); skip the interview and follow the Procedure with the yolo adjustments.

**Entry through a change request — triage first:** if the human asks to apply, execute, fix, or finish something and no active card exists, apply the **rule-13 triage** of [[AGENTS|AGENTS]] before creating a task: scope evident from the request itself + no new durable contract + no planning interview + fits in one session → it is a **direct fix** ("Direct fix" section of [[WORKFLOW|WORKFLOW]]: no card, proof in an `F-` memory ledger + specs) and this skill does not run. Any "no" → kanban (recommended when the change is large) or, if the user opts out of the kanban, the **no-kanban route** of [[WORKFLOW|WORKFLOW]] (the coding agent's plan mode, tracking always in `D-` memory + specs, no yolo) — and this skill does not run. “Start the flow in yolo” sets `yolo: true`, confirms materialization/release, and chains the entire yolo route. Reuse everything already answered in the conversation and ask only about an indispensable project/origin ambiguity; yolo or a roadmap/modifications item → kanban by default, with a one-line notice to the user.

**Delegate to subagents:** almost nothing — it is a short interview with the user; delegation begins at planning (`advance-task`).

## Interview (skip what the user already answered)

1. **Where:** which project, and does it come from the roadmap (a phase) or from modifications? If the user doesn't know, show the in-progress phases of the current epoch and propose the next natural task. **Hotfix, one-off tweak, contract fix/change or emergent feature outside the plan:** propose a **modification** — apply the 3-question frontier of [[AGENTS|AGENTS]] (fits in ~3 tasks? fits in a card without a planning interview? only touches existing contracts? — any "no" → roadmap via `plan-roadmap`). **Only the human creates a modification:** propose `M-<n>` (next free number, never reused — check MODIFICATIONS.md, the kanban and memory) and confirm; suggested `size` default `S`.
2. **What and why:** what does the task deliver, in one line? Why now — what does it unblock?
3. **Dependencies:** which tasks must be completed before this one (`depends_on`)? Look at the epoch/modification's tasks and propose; empty = can run in parallel with the others. (Gate: it only enters 004 with all of them completed — see WORKFLOW.) The `phase-verification` task depends on **all** the phase's other tasks; if the phase does not have it in the table, propose creating it (section "Phase verification" of the WORKFLOW).
4. **Criticality:** does this task also require human approval at verification (`critical: true`)? Consider the project's default in the sheet (PROJECT.md).
5. **Specs and research:** which durable contracts does it affect? Link an existing spec; create a draft through `write-spec` only if it introduces durable behavior, interface or invariant. A technical decision without prior research gets a `RESEARCHES.md` prompt before 002.
6. **Size:** does the change fit in **one cohesive brief** (≤~150 lines, preferably much less)? Independent objectives or too many fronts for a readable DAG → propose tasks chained by `depends_on` — in a modification, multi-task gets its own file in `pop/modifications/`.
7. **Effort (`size`):** propose `S | M | L` by delivery volume, with one-line rationale. Size alone does not choose topology: risk, skills, dependencies and write sets determine one executor or fronts/waves; planner and reviewer remain separate.
8. Propose the **id and slug** — roadmap: `<n>.<m>.<t>-<slug>` (`t` is the next free number in the phase); modification: `M-<n>.<t>-<slug>` (`t` is the next free number in the modification, starting at 1). Kebab-case slug, unique in the scope. Confirm.

## Procedure

1. Confirm the task exists (or add it) in its origin:
   - **Roadmap:** the phase table in `pop/roadmap/<n>-<epoch-slug>.md`.
   - **Modifications:** if `pop/MODIFICATIONS.md` doesn't exist yet, create it from `_templates/MODIFICATIONS.md` and add the `M-<n>` line. A **multi-task** modification also gets `pop/modifications/m-<n>-<slug>.md` from `_templates/MODIFICATION.md`, listing the task there; a **single-task** modification lives only in the MODIFICATIONS.md line.
2. Create the folder `pop/kanban/001_initial_task/<id>-<slug>/` (a scope whose harness lives at its own root: the same paths, without the `pop/` prefix) with the card `<id>-<slug>.md` copied from `_templates/TASK.md`:
   - Full frontmatter (`id`, `project`, `origin`, `epoch`/`phase` **or** `modification`, `stage: 001_initial_task`, `critical`, `yolo`, `size`, `blocked: false`, `depends_on: [...]`, `awaiting_merge: false`, dates) — delete the block of the unused origin.
   - **Resolve the yolo inheritance** (epoch → phase → task marker, or modification → task marker; the ` · yolo: no` opt-out wins): inherited/marked → `yolo: true` + a Log line with the origin (`yolo inherited from phase X.Y` / `yolo inherited from modification M-N`).
   - **Stamp the `size`:** the ` · size:` marker of the task's line in the origin, or the interview's suggestion (yolo mode without a marker: suggest it yourself) — always with a 1-line justification in the Log (`size M suggested: <reason>`). The human corrects it freely in 001.
   - "What", "Why", the "Dependencies" section and spec links filled in with the interview answers; first Log line.
   - The **Release** section stays with `- [ ] Ready to plan` **unchecked** — the card is born unreleased. **Exception:** a `yolo: true` task is born **checked**, with Log `released by yolo (marked on the roadmap/modifications)`.
3. In the epoch or modification table (or the MODIFICATIONS.md line, if single-task), turn the task id into the wikilink `[[<id>-<slug>]]` and update the status to `001_initial_task`.
4. If it is the project's first active task, check whether the project status in the INDEX files (category + root) should change to "in progress".
5. Close by pointing at the **release gate**: the card stays in 001 until the human checks `- [x] Ready to plan`. Explicit “create and advance” may check it with a Log entry and chain to 003; “start the flow in yolo” or `yolo: true` may check it, record the source, and chain the yolo flow (single gate at 005; 003 only for `critical`). None of these exceptions waives the card.

## Cautions

- **Read the project's AGENTS.md before creating:** constraints declared there apply — e.g. the organization gate of an imported project (Epoch 1 open → harness tasks only: specs, skills, researches, notes in `pop/`).
- Task files are linked **by name only** (`[[1.1.1-user-table-creation]]`, `[[M-1.1-adjust-contract]]`), never by path — the folder moves between stages.
- Don't write the plan here — that happens in `002_planning` via the `advance-task` skill.
