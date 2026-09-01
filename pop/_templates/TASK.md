---
id: <n>.<m>.<t>
project: <project>
origin: roadmap
epoch: <n>
phase: "<n>.<m>"
modification:
stage: 001_initial_task
critical: false
yolo: false
size: S | M | L
blocked: false
blocked_reason:
depends_on: []
claimed_by:
claimed_at:
worktree:
pr:
awaiting_merge: false
yolo_003_returns: 0
yolo_005_returns: 0
return_kind:
circuit_breaker: false
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# <id>-<slug> — <short title>

> Blockquotes in this template are fill-in instructions — **delete them when filling it in**. Harness paths carry the `pop/` prefix; a scope whose harness lives at its own root does not.
> **Origin:** a roadmap task (`origin: roadmap`) uses id `<n>.<m>.<t>` and fills `epoch`/`phase` (delete `modification`); a modification task (`origin: modifications`) uses id `M-<n>.<t>` and fills `modification: M-<n>` (delete `epoch`/`phase`).
> **Machine fields:** `yolo_*_returns`, `return_kind` and `circuit_breaker` are born empty/zeroed and are written **only** by `pop_move`/the orchestrator — editing them by hand inflates counters and makes the gate pick the wrong review mode.

- **Origin:** [[pop/roadmap/<n>-<epoch-slug>|Phase <n>.<m>]] — *or* [[pop/MODIFICATIONS|M-<n>]] for a modification task.
- **Plan:** [[<id>-<slug>.plan]] · **Approval:** [[<id>-<slug>.approval]] · **Verification:** [[<id>-<slug>.verify]]

## What

One or two sentences about the observable delivery, without anticipating implementation.

## Why

One sentence: why now, and what it unblocks.

## Release (user)

> Only the human checks it, except under an explicit command recorded in the Log. Without `[x]`, the task does not leave 001. For `yolo: true`, advance release from the roadmap/modifications or the human request “start the flow in yolo” lets the agent check it and record the source; yolo never waives the card or any remaining stage — see [[WORKFLOW|WORKFLOW]].

- [ ] Ready to plan

## Skills per stage

> Fill 002 at creation, and 004 and `005_closing` during planning. The `005_closing` row only applies to `yolo: true` — outside yolo the gate is the human PR. List only skills that change how the owner should work.

| Stage | Project skills | Owner |
|-------|----------------|-------|
| 002_planning | [[pop/skills/<skill>\|<skill>]] | agent |
| 004_processing | [[pop/skills/<skill>\|<skill>]] | agent |
| 005_closing | [[pop/skills/<skill>\|<skill>]] | agent |

## Dependencies

> Mirrors `depends_on:`. A missing dependency blocks execution; it does not authorize the agent to implement it. Empty = no kanban prerequisite.

- [[<id-of-prerequisite-task>]] — delivery required to start this task.

## Links

> Every link carries a trigger: when it is worth following.

- **Spec:** [[pop/specs/<spec>|<spec>]] — *follow to understand <contract/invariant>*.
- **Related task:** [[<id-of-another-task>]] — *follow if <condition>*.

## Log

- YYYY-MM-DD — created in 001_initial_task — <reason/origin>

## Minimal telemetry

> One row per completed/returned stage. Record observable cost, never reasoning, prompts, or discarded attempts.

| Stage | Contexts | Returns | Tests/strategy | Duration | Result |
|-------|----------|---------|----------------|----------|--------|
| 002 | planner: 1 | 0 | n/a | <e.g. 20min> | plan created |
