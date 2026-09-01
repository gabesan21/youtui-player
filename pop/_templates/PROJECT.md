# <Project name>

- **Status:** idea | planning | in progress | paused | completed | abandoned
- **Priority:** high | medium | low
- **Created on:** YYYY-MM-DD
- **Roadmap:** [[pop/ROADMAP|Roadmap]]

## Goal

One or two sentences: what does success look like for this project?

## Context

What an agent needs to know before working on this: history, motivation, current state of the world.

## Folder structure

Standard anatomy (see the root AGENTS.md): the project's `AGENTS.md` + `.agents/skills/` at the root; **all the harness in `pop/`** — `pop/PROJECT.md` + `pop/ROADMAP.md` + `pop/roadmap/` (epochs), `pop/researches/` (research by topic), `pop/skills/`, `pop/specs/`, `pop/notes/` (learnings/decisions/ideas/references), `pop/memory/` (summaries of completed tasks), `pop/worktrees/` (gitignored), `pop/kanban/` (stages 001–`005_closing` of the [[WORKFLOW|WORKFLOW]]); the **project content** (code, manuscript, clones — per the type, [[TYPES|TYPES]]) lives directly at the root. List here only what deviates from the standard.

## Agent harness

Project-specific rules for agents working on this project:

- **Type and repositories:** declared in the [[AGENTS|project AGENTS]] — where the content lives, which repos exist and what the PR branch is (`uni-repo` | `multi-repo`, see [[TYPES|TYPES]]).
- **Worktree per task:** yes (default) | no (acceptable only in a project without a git repository — tasks lose isolation and the PR).
- **Tools and restrictions:** what is allowed and what is not.
- **Tone/style:** if applicable.
- **Tasks critical by default?** yes | no — and what makes a task critical in this project (extra human gate in 005, see [[WORKFLOW|WORKFLOW]]).
- **Skills:** list the skills in `pop/skills/` with one line on when to use each.

## Related projects

- [[pop/PROJECT|<name>]] — why they relate.

## Decisions

- **YYYY-MM-DD:** decision made and rationale. (If it grows, extract into its own note in `pop/notes/`.)
