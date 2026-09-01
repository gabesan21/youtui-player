# Epoch <n> — <epoch name>

> Blockquotes in this template are fill-in instructions — **delete them when filling it in**.

- **Project:** [[pop/PROJECT|<Project name>]] · **Roadmap:** [[pop/ROADMAP|Roadmap]]
- **Status:** pending | in progress | completed
- **Description:** one line — what this chapter delivers.
- **Yolo:** yes | no — **optional** bullet (absent = no); only the human marks it.
- **Abort/pause if:** objective condition, if any (audited by the `weekly-review`).

> One phase per section; under each phase, only still-open tasks — **always one-line descriptions**. On closing the `005_closing` stage, remove a task row only after its canonical memory is valid; preserve the epoch, phase, and other open tasks.
> **Yolo inherits:** a yolo epoch → phases and tasks inherit; a yolo phase → tasks inherit. Per-task opt-out/opt-in: append ` · yolo: no` (or ` · yolo: yes`) to the end of the Description cell — no new column. `new-task` resolves the inheritance and stamps the card (Yolo mode section of [[WORKFLOW|WORKFLOW]]).
> **Size:** the agent suggests `S|M|L` in the Description; `new-task` stamps it on the card and the human corrects it in 001. Size guides tier/effort; risk, skills, dependencies and write sets determine topology in [[WORKFLOW|WORKFLOW]].

## Recon and forks

> Researches in `pop/researches/` (a scope whose harness lives at its own root: without the `pop/` prefix) that grounded the breakdown; whatever remained unanswered is RECON NEEDED, with the check that resolves it. Forks: pre-identified route changes.

- [[pop/researches/<topic>/<note>|<topic>]] — what it established, in one line.
- [ ] RECON NEEDED: <assumption> — check: <research/experiment/task that resolves it>.
- Fork: if <observation/conclusion X> → <what changes in the epoch, in one line>.

## Phase <n>.1 — <phase name>

- **Status:** pending | in progress | completed
- **Description:** one line.
- **Yolo:** yes | no — **optional** bullet (absent = inherits from the epoch).
- **Specs:** [[pop/specs/<spec>|<spec>]]

| Task | Description (≤1 line) | Status |
|------|-----------------------|--------|
| `<n>.1.1-<slug>` | What it delivers. · size: M | not started |
| [[<n>.1.2-<slug>]] | What it delivers (linked: already exists in the kanban). | 002_planning |
| `<n>.1.3-phase-verification` | Writes/runs the phase's suite (`verify: phase` criteria) and fixes what it catches. · size: M | not started |

> **Every phase ends with the `phase-verification` task** (`depends_on` all the others): it is the only one in which tests run — section "Phase verification" of the [[WORKFLOW|WORKFLOW]].

## Phase <n>.2 — <phase name>

- **Status:** pending
- **Description:** one line.

| Task | Description (≤1 line) | Status |
|------|-----------------------|--------|
| `<n>.2.1-<slug>` | ... | not started |
