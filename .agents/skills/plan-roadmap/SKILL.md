---
name: plan-roadmap
description: Guided interview to build or evolve a project's roadmap (epochs, phases, candidate tasks). Use when creating a new project, when the user wants to plan/restructure the roadmap, or when an epoch completes.
---

# plan-roadmap

Builds the roadmap **together with the user**, by interview — never invent the path on your own. Works for any kind of project (programming, writing, business, research...).

**Delegate to subagents:** step 4's epoch recon (parallel, one per front); the interview and materialization stay with the main agent.

## How to conduct

- Ask in short blocks (2–3 questions at a time), reflect back what you understood before moving on.
- **Propose, don't interrogate:** from the goal, suggest the epochs yourself and let the user react — reacting to a proposal is easier than answering an open question.
- "I don't know" is a valid answer → it becomes an item in "Future ideas" or an open question in a spec.

## Procedure

1. **Destination:** ask what the final milestone is and what the first delivery that would already have value on its own would be.
2. **Epoch brainstorm:** propose 3 to 7 epochs (chapters of the project), one line each, in the order that makes sense. Ask for reactions: cut, merge, reorder, rename.
3. **Cut:** what doesn't make it now goes to "Future ideas" in ROADMAP.md — better a short list of firm epochs than a long wish list.
4. **Epoch recon:** before detailing, gather what underpins the chapter **in the current scope and its repos** — subagents only for fronts above rule 18's floor (0 is valid) — and consolidate in `pop/researches/<topic>/`. What the recon doesn't resolve becomes **RECON NEEDED** in the epoch file, with the exact check that resolves it (research, experiment or task). New knowledge (technical decision, market, stack) **is not researched on the web in the flow**: propose the prompt in the project's **`RESEARCHES.md`** (`_templates/RESEARCHES.md`) for the **user** to run and ingest (`ingest-research`) before the planning that depends on it.
5. **Progressive elaboration:** detail into phases **only the first epoch** (or the current one). Future epochs stay as a single line — they'll be detailed when their turn comes. Record in the epoch file the known **forks** ("if research X concludes Y, phase Z changes like this") and the **abandon/pause condition**, if any (the `weekly-review` audits it). Ask whether any epoch/phase runs in **yolo** (Yolo mode section of the [[WORKFLOW|WORKFLOW]]) and record the `**Yolo:** yes` bullet (or per-task markers) — a yolo scope requires tasks with an **objectively verifiable** deliverable, which affects the candidates' granularity.
6. **Candidate tasks:** for the first phase, propose 2–5 one-line tasks, each with the **suggested effort** ` · size: S|M|L` in the Description cell (the [[_templates/EPOCH|template]] convention) — `new-task` stamps it on the card and the human corrects it in 001. **Every phase ends with the verification task** (slug `phase-verification`, last in the table, `depends_on` all the others): it is in it — and only in it — that the phase's tests are written and run, covering the accumulated `verify: phase` criteria (section "Phase verification" of the [[WORKFLOW|WORKFLOW]]); always propose it, without asking. Don't create the kanban folders — that's the `new-task` skill.
7. **Specs:** note the topics that surfaced in the conversation and deserve a specification; offer to create the drafts with the `write-spec` skill.
8. **Materialize:** `pop/ROADMAP.md` (epochs only) and `pop/roadmap/<n>-<slug>.md` for the detailed epoch (a scope whose harness lives at its own root: the same paths, without the `pop/` prefix), from the `_templates/ROADMAP.md` and `_templates/EPOCH.md` templates. Confirm the result with the user.

## Cautions

- Descriptions are **always one line** — detail goes to a spec.
- The execution brief (strategy, fronts, ownership, risks and criteria) belongs to task planning in 002 — the roadmap keeps only description, dependencies and context that changes prioritization.
- Applications: the **supported languages (i18n)** declared in the project's AGENTS.md enter the planning — no UI or content epoch/phase ignores i18n.
- Don't detail future epochs "to get ahead": the roadmap is elaborated progressively; revisit this skill at each completed epoch.
- IDs follow the hierarchy (`1`, `1.1`, `1.1.1-<slug>`); links to fixed files use full path + alias.
