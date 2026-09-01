---
task: <id>-<slug>
entry: <nn>-<entry-slug>
---

# <short title: the thing done>

> **Memory entry.** It lives in `memory/<YYYY-MM-DD>/<id>-<slug>.<nn>-<entry-slug>.md`, in the same folder as the task [[_templates/MEMORY|ledger]], which indexes it under `## Entries`. Ceiling: **800 characters**. An entry the ledger does not link is orphaned and fails validation.
> `<nn>` is a two-digit sequence (`01`, `02`…) in the **chronological order of what happened**, not in order of convenience. Renumbering breaks the timeline.
> One entry = **one thing done**. Changed areas, telemetry, a durable decision and a deviation are each their own entry, not bullets squeezed into a single file. If it does not fit in 800 characters, it is almost always two entries.
> Do not retell the plan or the execution narrative, do not invent history, and do not replace a pointer with a summary.

<Two to four sentences: what was done and why this way. Fact, not a trial-and-error narrative.>

## Evidence

> **Mandatory: at least one wikilink.** It is what turns the entry into proof instead of assertion. Point at the spec the work changed or the file it touched — a wikilink to a non-markdown file is valid and desirable.

- [[specs/<spec>|<spec>]] — *follow for the contract this change altered*.
- [[pop/scripts/<file>.py]] — *the file where the change lives*.
