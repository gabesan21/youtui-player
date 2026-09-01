---
task: <id>-<slug>
project: <project>
started: YYYY-MM-DD
finished: YYYY-MM-DD
commit: <final-commit-hash>
pr: <PR-link-or-explicitly-empty>
authorization: <D-YYYYMMDD-<slug>: no-kanban route (plan mode) chosen in the triage · F-YYYYMMDD-<slug>: direct-fix triage (rule 13)>
---

# <id>-<slug> — <short title>

> The task **ledger**: the file that proves it finished. It lives in `memory/<YYYY-MM-DD>/<id>-<slug>.md`, and the **folder is the completion date — equal to `finished`**. Ceiling: **1200 characters**.
> The ledger does not tell what was done; it identifies, attests and **indexes**. What was done lives in the **entries** alongside it, `memory/<YYYY-MM-DD>/<id>-<slug>.<nn>-<entry-slug>.md` ([[_templates/MEMORY-ENTRY|MEMORY-ENTRY]]) — one thing done per file, ≤800 characters, each with an evidence wikilink. That granularity is what allows optimizing later with [[.agents/skills/optimize-memory/SKILL|optimize-memory]] without rereading the whole memory.
> Changed areas, telemetry, durable decisions and deviations are **not** bullets here: they are entries.
> Work through the no-kanban route (the coding agent's plan mode) uses `task: D-YYYYMMDD-<slug>`; a **direct fix** approved by the rule-13 triage uses `task: F-YYYYMMDD-<slug>`. Both fill `authorization` and have no card or roadmap/modifications row — but they have a ledger and entries like any other.

- **Delivery:** <one sentence: what came to exist or changed>.
- **Verification:** <aggregate gate and result>.
- **Contract impact:** specs: <assessed; updated when affected> · DOX: <assessed; updated when affected>.

## Entries

> One line per entry, in chronological order, each saying what that file tells. An entry not linked here is orphaned and fails validation.

- [[<id>-<slug>.01-<entry-slug>]] — <what was done, one line>.
- [[<id>-<slug>.02-<entry-slug>]] — <what was done, one line>.

## Links

> Every link carries a trigger: when it is worth following. Evidence of a change belongs to the entries; whole-task pointers live here.

- **Origin:** [[pop/roadmap/<n>-<slug>|Phase <n>.<m>]] — *follow for the context that asked for the task*.
- **PR/commit:** <link or hash> — *follow to inspect the final diff*.
