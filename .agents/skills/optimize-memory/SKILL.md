---
name: optimize-memory
description: Converts legacy memory into the granular layout (date folder + ledger + entries with evidence) and trims any file over the cap, without losing identity, evidence, chronology, or critical decisions. Runs outside the kanban and in waves of parallel subagents. Use on explicit request, when a ledger exceeds 1200 or an entry 800 characters, when memory sits outside a date folder, or on weekly-review candidates.
---

# optimize-memory

Make `memory/` granular and verifiable without turning it into a changelog or erasing proof. The unit remains **one ledger per task**: never merge, delete, or rename memories.

**It always runs outside the kanban.** `memory/` is the scope's own harness, not content: do not create a card, do not use `new-task`, do not open a task branch, worktree or PR, and do not move any task ("Current scope" › three classes, in [[WORKFLOW|WORKFLOW]]). Invoked by [[.agents/skills/weekly-review/SKILL|weekly-review]], you are a worker of its correction wave, with the scope already carved out.

**Delegate in parallel waves.** The main agent does the preflight, distributes and validates; it does not convert file by file by hand. One worker per **task** (the ledger and the entries born from it are a single write set), in waves of 3-5, with **disjoint** write sets — two workers never receive the same date folder. Each worker returns the paths it wrote and the character counts; no worker spawns subagents or decides to reclassify what it received. A single small file is done directly: a wave for one task is ceremony with no gain.

## Target layout

```
memory/YYYY-MM-DD/<id>.md              ← ledger: proof + index, ≤1200 characters
memory/YYYY-MM-DD/<id>.<nn>-<slug>.md  ← entry: one thing done, ≤800 characters
```

The folder is the completion date and **must equal the ledger's `finished`**. The ledger keeps the intact frontmatter, delivery, verification, contract impact, `## Entries` (one line per entry, chronological) and `## Links`. Each entry carries `task` + `entry` frontmatter, what was done in two to four sentences, and **at least one evidence wikilink** — the spec changed or the file touched. Form: [[_templates/MEMORY|MEMORY]] and [[_templates/MEMORY-ENTRY|MEMORY-ENTRY]].

## Preflight and irreducible data

Classify each file into one mode: **convert** (flat memory in `memory/<id>.md`, or a ledger holding what should be entries) or **trim** (ledger or entry over the cap, already in the layout).

For every file, inventory path, `task`, `project`, `started`, `finished`, `commit`, `pr`, event order, and durable decisions. Missing required fields or ambiguous chronology is **BLOCKED**—do not infer and do not convert.

Preserve all frontmatter; task identity; dates; commit and PR (including an explicit empty value); the order of start, delivery, verification, integration/PR, and finish; delivered result; final verification; contract-changing deviations; critical decisions and rationale; and valid triggered links.

A critical decision constrains future behavior or records a human choice, security, compatibility, ownership, migration, irreversibility, or approved deviation. When uncertain, preserve it.

## Convert mode

1. Move the file to `memory/<finished>/<id>.md`, using the `finished` of its own frontmatter — never today's date, never inferred.
2. Reduce the ledger to delivery, verification, contract impact, `## Entries` and `## Links`.
3. Turn what came out into entries: changed areas, telemetry, every durable decision, every deviation. **One thing done per file**, numbered `01`, `02`… in the chronological order of the events.
4. Give each entry its evidence. An entry whose change has no spec and no file to point at almost always belongs to another entry — merge before inventing a link.
5. Index every entry under the ledger's `## Entries`, one line saying what it tells.

## Trim mode — what may be compacted

- Repeated plan text, edit steps, and trial-and-error narrative.
- Long file lists that one subtree plus a sentence can replace.
- Duplicate evidence when the final command/result preserves proof.
- Context already held by a linked spec/decision, retaining one sentence and its trigger.

An entry that still does not fit in 800 characters is almost always **two entries** — splitting beats compressing. A ledger over 1200 is holding entry content: move it, do not squeeze it. Write short facts in chronological order. Do not add history, reinterpret decisions, or replace pointers with prose.

## Safe procedure

1. Produce a candidate keeping the frontmatter and the templates' structure.
2. Compare it with the preflight inventory; any irreducible loss rejects it.
   - **The comparison is deterministic, not a reading impression.** Extract from the original every commit hash (including those cited in the body, not only the frontmatter one) plus the literal `pr` and `authorization` values, and check that all of them appear in the candidate. A token present before and absent after is loss, even when the text looks equivalent — that is how one conversion lost 8 hashes on 2026-07-27.
3. **Measure the candidate before writing it**, with `wc -c` — not afterwards, and not by eye. The caps are ≤1200 per ledger and ≤800 per entry; **1201 is a violation**, and writing only to discover that later leaves the scope worse than it was. Confirm as well `YYYY-MM-DD` dates and the folder equal to `finished`.
4. Validate wikilinks — including each entry's evidence — and run `python3 pop/scripts/pop_validate.py`. The validation belongs to the **main agent**, after every wave: a worker that validates alone approves its own slice without seeing the collision.
5. Review each diff; on failed preservation, restore the original and report **BLOCKED**.
6. A backup, if you make one, lives **outside** `memory/` — inside it, a folder that is not a date is a layout violation, and you would have traded one debt for another. Delete it when closing; the durable proof is Git.

Report paths, entries created, before/after character counts, preserved fields/decisions, and validations. If no material safe gain exists, leave the file unchanged and record "no safe optimization". Do not edit specs, decisions, roadmaps, cards, code, or Git; do not consolidate memories per epoch/phase; flat memory finished before 2026-07-27 outside the current scope is tolerated legacy and not your work. Never create inside `memory/` any folder that is not a completion date — backups, archives and drafts stay outside it. In the `weekly-review`, the collection front only measures and lists; converting is always this skill, with the scope carved out.
