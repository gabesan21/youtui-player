---
name: weekly-review
description: Periodic review of the current scope - sweeps epochs, modifications and tasks, fixes the harness wherever the call is unambiguous and proposes the rest. Always runs outside the kanban and in waves of parallel subagents. Use when the user asks for a roadmap review or an overview of the work.
---

# weekly-review

Measures the **current scope**, **fixes** what is unambiguous and proposes what requires a decision.

**It always runs outside the kanban.** Do not create a card, do not use `new-task`, do not open a task branch, worktree or PR, and do not move any task. Reviewing harness is maintenance of the material the kanban consults — submitting it to the kanban is asking the process to approve itself (rule 13 and "Current scope" in [[WORKFLOW|WORKFLOW]]).

## The boundary: what this skill fixes

The file's class decides, never the size of the finding ("Current scope" › three classes):

- **Managed harness** (`WORKFLOW.md`, `_templates/`, `pop/scripts/`, `.agents/skills/`) → **never edit it**. Staleness is resolved by reinstalling from the origin; the review performs the reinstall when that is the remedy, because it is mechanical and idempotent, and it **reports** any other finding in this class.
- **The scope's own harness** (`AGENTS.md`, `PROJECT.md`, `roadmap/`, `specs/`, `notes/`, `skills/`, `memory/`) → **fix directly** whatever is unambiguous: a dead link, a reference to a nonexistent stage, a file over the cap (slice it), a passage that belongs in a spec/note/memory, memory outside the layout (via [[.agents/skills/optimize-memory/SKILL|optimize-memory]] within the scope). Every fix is a small, reversible edit, with the file named in the report.
- **Project content** (code, manuscript) → **never**, under no circumstances: report only.

**Propose, don't fix**, even inside the scope's own harness, when the fix **changes meaning**: rewriting a spec contract, promoting a modification to an epoch, abandoning/pausing an epoch, changing a project's status, deleting a record. Rule of thumb: if two reasonable people would disagree with the outcome, it is a proposal.

**The target is always the current scope** ("Current scope" section of [[WORKFLOW|WORKFLOW]]): the root holding the `AGENTS.md` you are reading. "Overview" never means leaving it. If an `origin-scope.md` sits next to this file, the scope hosts others and gains the extra fronts described there; if it does not exist, those fronts **do not apply** — do not look for them and do not invent them.

**The normal flow reviews the base harness, never the projects.** When the current scope hosts others, the review covers the root scope alone; the hosting fronts look at projects from the outside (freshness, indexes, drafts) without sweeping any project's internals. A project is only reviewed when the human **explicitly orders it** — and then the review runs **from inside that project** (its own `AGENTS.md` as the current scope), never as a side front of the root review.

**Delegate in parallel, mandatorily.** The main agent runs step 1's scripts, launches the waves of steps 2 and 3 and consolidates — it never sweeps or fixes by hand. Collection and correction are **waves of parallel subagents**, and no worker spawns subagents.

## Procedure

1. **Scripts first:** run `pop/scripts/pop_status.py` (kanban overview, blocked tasks, pending gates — 003, review/human in `005_closing`, `awaiting_merge`, >14 days) and `pop/scripts/pop_validate.py` (limits, frontmatter and warnings). INBOX.md is Dataview, not a source.
   **Harness version:** `python3 pop/scripts/pop_install_unirepo.py --check-fresh .` reports the version installed here. Comparing it against the origin is the job of whoever installed it — it is not a finding of this review and it never justifies going looking for the origin.
2. **What the scripts don't cover → parallel subagents**, one per front, in **waves of 3-5**, each with a specific question and an answer ≤30 lines with a **source per finding** and a "Gaps / Not found" section (workers spawn no subagents):
   - **Base files:** measure `AGENTS.md` and `pop/PROJECT.md` against the **~60 line** cap for the project AGENTS.md. In an application, **discount the DOX block and measure the rest** — `pop_validate` already reports that number as a warning, and it is the target: an exemption that switches the measurement off hides debt. Classify every excess passage by **destination**, using the "what must not go in" of [[_templates/AGENTS-PROJECT|AGENTS-PROJECT]] as the criterion: flow narration → a **triggered pointer** to [[WORKFLOW|WORKFLOW]]; a contract, invariant or durable interface → a line in a spec; the reason for a choice → a note in `notes/decisions/`; an event → it already lives in `memory/`. A cheap symptom: a reference to a nonexistent stage (`005_verifying`, `006_done`) — `grep` proves the duplicated text rotted. **Replacing a passage with a pointer and fixing a rotten reference are fixes** (the scope's own harness); moving text into a spec that then promises something new is a proposal.
   - **Orphaned worktrees:** `pop/worktrees/` with content whose task is not in `004`/`005_closing` awaiting merge.
   - **Outdated specs:** the `sync-specs` skill's audit (tasks in done whose specs weren't updated).
   - **DOX audit:** in an application with a DOX tree ([[_templates/DOX|template]]), obsolete contracts (purpose/structure/flow changed without an update), dead links and blown caps (~60 lines, ~3 laterals, <7 references per contract).
   - **Note health:** orphan notes (no inbound wikilinks in the scope) and contradictions between notes/decisions and specs — reply ≤15 lines: candidates to link, merge or mark with `> Contradicts:`.
   - **Memory, roadmap and modifications health:** completed-task residue reported by `pop_validate`; memory still flat outside a date folder, a ledger over 1200 or an entry over 800 characters, an entry with no evidence, a folder inside `memory/` that is not a date (a conversion backup lives **outside** `memory/`). This front **measures and lists the files**; the fix is [[.agents/skills/optimize-memory/SKILL|optimize-memory]], invoked in step 3 with that scope — it is the one that knows how to preserve proof, and no collection worker converts memory on its own. Residue in the roadmap/modifications of an already-completed task is a direct fix (remove the row), and **a completed modification is a direct fix: remove its whole row from MODIFICATIONS.md — no log remains, the durable record is memory + specs** (check first that each of its tasks has a ledger); the status of a still-open epoch/modification is a proposal.
   - **Stalled epochs:** "Abandon/pause if" conditions met in the epoch files; Epoch 1 (Organization) still open — since when and what is missing to release the gate.
   - **Dated debt of the adversarial gate:** the "Transition — a card older than the gate" clause of act 1 of `005_closing` ([[WORKFLOW|WORKFLOW]]) and the `GATE_ADVERSARIAL_SINCE` constant that implements it in the validator exist **only** for cards that went through 002 before the gate came into force — they are debt, not a permanent rule. Measure with a command, not by impression:
     ```sh
     CUT=$(grep -hoE 'GATE_ADVERSARIAL_SINCE = "[0-9]{4}-[0-9]{2}-[0-9]{2}"' \
       pop/scripts/pop_validate.py pop/scripts/pop_validate.py 2>/dev/null \
       | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -1)
     case "$CUT" in [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]) ;; *) CUT= ;; esac
     if [ -z "$CUT" ]; then
       echo 'ERROR: cut-off date not found — the debt CANNOT be removed' >&2
       false
     else
       grep -rH '^created:' kanban pop/kanban 2>/dev/null \
         | awk -F'created: ' -v c="$CUT" 'NF>1 && $2 < c {sub(/:$/,"",$1); print $1}'
     fi
     ```
     The command covers both anatomies (harness at the root itself and in `pop/`) and **fails closed**: with no readable constant it prints the error and exits with a non-zero status, never reaching the `awk`.
     **Removal trigger:** empty output **and** a zero exit status — an error is never a trigger, and empty output with a non-zero status means the measurement did not happen. With the command successful, empty output means no pre-cut-off card in any kanban stage and no in-flight task with a `created:` earlier than the cut-off. Then the front proposes the **joint** removal: the clause in [[WORKFLOW|WORKFLOW]], the caveat in the gate spec, the constant and the exemption in the validator, and the tests that cover them. A partial removal is worse than none — the proposal is always of the whole set. While a pre-cut-off card exists, the front only reports how many and which, and proposes nothing.
   - **Swollen modifications:** a modification with more than ~3 open tasks or open for too long → proposal of promotion to a roadmap phase/epoch via `plan-roadmap` (open tasks conclude as `M-`; only the not-yet-tasked work migrates — frontier in [[AGENTS|AGENTS]]).
   - **Orphaned yolo:** external working branches whose yolo scope stalled (blocked tasks or a scope closed without the final PR — which the agent only suggests and opens on human request). A local scope is exempt because it delivers directly to `main`.
3. **Correction wave → parallel subagents, one per group of files.** With the findings in hand, the main agent separates whatever the boundary above classifies as a **fix** and distributes it:
   - **Disjoint write sets are a prerequisite for the parallelism.** Two workers never receive the same file; findings that touch the same file become **one** worker. Without this, the corrections overwrite each other and the parallel gain turns into rework.
   - Each worker receives: its findings with path and line, the destination of each passage, the file's cap, the "do not do X" boundary (no content, no managed harness, nothing that changes meaning) and the order to return the list of what it edited. A worker never reclassifies a finding: whatever does not fit the instruction comes back as a proposal.
   - **The reinstall and `optimize-memory` are workers of this wave**, each with its own scope — not chores of the main agent.
   - The main agent **validates before closing**: `pop_validate` on the current scope and a file-by-file read of the diff. A fix that introduces a violation is reverted and reclassified as a proposal.
4. **Consolidate:** the main agent assembles the report from the scripts and the workers' answers. Write it in the current scope's `pop/notes/` (`notes/` when the harness lives at the root itself), with:
   - **Waiting on you**: pending human gates and `open` questions in `open_questions/`, with link and since when.
   - **Adjusted in this review**: each corrected file, what changed in one line, and the class that authorized the fix. An empty section is a legitimate answer.
   - **Stalled**: tasks without movement, with a suggestion (resume, pause, abandon) and a one-line justification.
   - **Progress**: what moved since the last review (compare with the previous report, if any).
   - **Proposals**: whatever requires a decision — promotions of ideas to epoch, epochs ready to complete, modifications to promote to the roadmap, contract rewrites, priority adjustments.
5. Link the report in INBOX.md ("Reviews" section) so the human can find it, and commit the corrections alongside it (rule 15) — one review commit, with a message saying it is harness maintenance.

## Cautions

- Report ≤150 lines; extra detail becomes a linked note.
- **Never move a task, change a `stage`, touch a card or touch project content** — not even to "tidy up". Those belong to the kanban, and the review is not of the kanban.
- A fix with no measured finding does not exist: every edit by this skill points to a line of the report and to the script or worker that found it.
- Remove review reports older than 3 months (or move them to an archive folder) when creating a new one.
- A finding that could only exist outside the scope does not enter the report: it becomes a question in `open_questions/`, or it does not exist.
