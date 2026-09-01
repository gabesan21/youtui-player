# Approval — [[<id>-<slug>]]

> Blockquotes are filling instructions — **delete them when filling**.

- **Stage:** 003_human_approval · **Owner:** user | independent reviewer in yolo `critical`

> One round per visit to 003. In yolo, this file only gets a 003 round when `critical: true` — a **strong** critic signs, returns 1–2 automatically go to 002 and failure 3 activates the circuit breaker; other yolo tasks transit 002 → 004 without a round. Never delete old rounds.

## Round 1 — YYYY-MM-DD

### Decision brief

- **Delivery:** <one line>.
- **Strategy:** <one or two lines>.
- **Topology:** <single executor or fronts/waves>.
- **Main risk:** <material risk or none>.
- **Main criteria:** <IDs or short summary>.
- **Plan:** [[<id>-<slug>.plan]] — *follow to review the complete brief*.

### Human response

_(write here: approved, or what to change)_

- [ ] Done

### Agent decision

_(after Done: `approved → 004` or `changes requested → 002: <summary>`)_

### Critic response (yolo)

- **Context:** independent strong.
- **Return:** 0 | 1 | 2 of 2.
- **Decision:** approved → 004 | returned → 002 | circuit breaker.
- **Reason/evidence:** <objective, no reasoning>.

## Merge — 005_closing — YYYY-MM-DD

> Created when the applicable flow requires human merge. **Outside yolo, reviewing this PR is the verification** — there is no agentic reviewer, and no memory, spec sync or roadmap cleanup happens before the `- [x] Done`. In yolo, follow [[WORKFLOW|WORKFLOW]] integration policy; do not invent another quality gate here.

- **PR:** <link> — `task/<id>-<slug>` → `<PR branch>`.
- _Without git: record the applicable final approval._

### Human response

_(merge, or explicitly authorize the agent)_

- [ ] Done

### Delta of the return

> Fill in **only** if you ask for a correction instead of merging. Partial re-entry is not a yolo privilege: naming the delta keeps a one-front correction from re-executing the whole task. The agent carries the type with `pop_move --return-kind <type>`.

- **Type:** lacuna (a criterion was missing; what was delivered is correct) | premissa (the strategy was wrong) | execucao (did not deliver what was agreed).
- **Affected criteria/fronts:** <IDs> — <what is missing, one line>.
- **Untouched fronts:** `<Fxx>` — do **not** re-execute.

### Agent decision

_(final commit, generated memory, removed worktree and closed task)_
