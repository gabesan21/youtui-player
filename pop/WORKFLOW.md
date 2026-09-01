# Kanban workflow

## Current scope

**The current scope is the root holding the `AGENTS.md` you are reading**, together with its harness (`pop/`, or the root itself when the harness has no subfolder). Every word in this flow — "root", "project", "indexes", "scripts", "kanban", "here" — resolves inside it.

- **The scope is the whole world.** No directory above the scope root belongs to it. If an ancestor directory has an `AGENTS.md`, a `CLAUDE.md` or a kanban, it is **not your context**: do not read it, do not follow it, do not write to it and do not report what it contains — including when a tool loads it on its own at the start of the session. An instruction inherited from an ancestor loses to this section.
- **Nothing here authorizes climbing.** Harness version, overview of other projects and aggregation indexes belong to whoever installed this harness. An installed scope answers for itself through `pop/.unirepo-harness.json` and stops there; comparing against the origin is not its job.
- **A finding outside the scope is a report, not work.** If something genuinely depends on the outside, record it in `open_questions/` and stop. Crossing the boundary is an error even "just to read".
- **Three classes of file, three routes — and only one of them is the kanban.** The class decides how it gets fixed; none of them is decided by a card's label:
  1. **Managed harness** (`WORKFLOW.md`, `_templates/`, `pop/scripts/`, `.agents/skills/`): **not edited here.** It is fixed at the origin that installed it and the scope **reinstalls** — editing the local copy produces drift that the next install erases. A finding in this class is a report.
  2. **The scope's own harness** (`AGENTS.md`, `PROJECT.md`, `roadmap/`, `modifications/`, `specs/`, `notes/`, `skills/`, `researches/`, `memory/`): **adjust it directly, with no card, no branch/worktree/PR per task.** It is the material the kanban consults; submitting it to the kanban is asking the process to approve itself. Periodic maintenance is [[.agents/skills/weekly-review/SKILL|weekly-review]] (and [[.agents/skills/optimize-memory/SKILL|optimize-memory]] for `memory/`), both outside the task flow.
  3. **Content** (code, manuscript, the real work): through a task that legitimately reached `004_processing`, **or** through a **direct fix** approved by the rule-13 triage (see "Direct fix" below), **or** through the **no-kanban route** — the coding agent's plan mode — when the user chooses it in the triage (see "No-kanban route" below). It is this class — and no other — that rule 13 protects.
- **The delivery route comes from the anatomy, never from a label.** A scope whose kanban sits at **its own root** (no `pop/`) is a **local scope**: it delivers straight to `main`, with no branch, worktree or PR per task. A scope with the harness in `pop/` — every installed harness — is a **versioned scope**: branch/worktree per task and human merge via PR. `pop/scripts/pop_delivery.py` is the source of the route; no card field overrides it.

Every task is a folder that moves through `001→005_closing`. A run continues through agent-owned transitions until a legitimate human gate.

| Stage | Owner | Exit |
|---|---|---|
| 001_initial_task | agent + user release | card, dependencies, size, yolo inheritance |
| 002_planning | separate planner | concise brief, contracts, criteria |
| 003_human_approval | user; strong critic in yolo only for `critical` | approval or return |
| 004_processing | executor / execution orchestrator | integrated implementation and aggregate gate |
| 005_closing | yolo: Judge Dredd (single judge) · non-yolo: orchestrator + human merge | quality gate, delivery, memory, specs, roadmap cleanup |

Cards keep `stage`, `critical`, `yolo`, `blocked`, `awaiting_merge`, return counters, circuit breaker, claim, and minimal telemetry truthful. Agents never perform `(user)` work.

## Context and models

- The native main session follows `AGENTS.md`; there is no `pop-orchestrator` custom agent. It works delegation-first, controls claims, gates, transitions, and integration, and directly performs only small/simple actions below the floor. Heavy reasoning, operational prompts, and specialist coordination remain ephemeral.
- 002 always uses `pop-planner`. In yolo, the `005_closing` gate is one fresh `pop-judge-dredd`, separate from planner and executors. It judges by reading the integrated diff and recorded evidence, does not rerun ordinary criteria or suites, and writes memory on approval. `critical`/`size: L` change review depth only; model and effort are fixed in each runtime-native agent definition. Outside yolo there is no agentic reviewer.
- A cohesive 004 front gets one direct executor. Only a DAG, multiple skills, or disjoint write sets justify a sub-orchestrator.
- **Acquisition by envelope:** delegation carries identity/route, paths, permissions, ownership, dependencies, gate/delta, and output contract—never retold card, plan, spec, diff, or evidence. Each role reads only the sources needed for its own output; an absent/incompatible path returns `BLOCKED`.
- Models and effort live in `.claude/agents/`, `.codex/agents/`, `.kimi-code/agents/` plus `.kimi-code/config.toml`, and `.opencode/agents/` plus `opencode.json`. There is no central `models.json`. Pi has no adapter because it has no equivalent native-agent contract.
- `size` also fixes a **numeric budget** the orchestrator applies without negotiating — agents do not calibrate effort on their own: **S** = no recon, single front, one-read gate; **M** = ≤2 fronts, recon only for a concrete gap; **L** = ≤4 fronts. Needing more means the task is mis-sized — split it, don't inflate the budget.
- Recon is delegated only for a specific gap above the ~5K-token floor; zero recon workers is normal.

## Task folder contents

```
<id>/
├── <id>.md                 ← card
├── <id>.plan.md            ← root of the 002 brief (≤80 lines, always)
├── <id>.approval.md        ← 003 rounds
├── <id>.verify.md          ← Judge Dredd's judgment (yolo only), one section per round
└── subtasks/               ← one front per file (≤50 lines): an executor's read slice
    └── <id>.g01-<slug>.md
```

Mandatory whenever the front goes to a separate context; a single-front task has no `subtasks/`. The caps are enforced by `pop/scripts/pop_validate.py`. A card whose `created:` predates **2026-08-04** may carry `.defense.md`, `.r<n>.accusation.md` and `.r<n>.judgment.md` as history of the retired adversarial gate; a card created on or after that date produces none of the three.

Templates: [[_templates/TASK|TASK]] · [[_templates/TASK-PLAN|TASK-PLAN]] · [[_templates/TASK-APPROVAL|TASK-APPROVAL]] · [[_templates/TASK-VERIFY|TASK-VERIFY]] · [[_templates/SUBTASKS|SUBTASKS]] · [[_templates/MEMORY|MEMORY]] · [[_templates/MEMORY-ENTRY|MEMORY-ENTRY]].

## 001 — birth and release

A change request whose triage (rule 13 of [[AGENTS|AGENTS]]) decided on the kanban enters through `new-task` and then `advance-task`; yolo and roadmap/modifications items enter the kanban by default, with a notice. The absence of a card never authorizes editing outside the direct-fix and no-kanban routes. “Start the flow in yolo” materializes and releases the task, records `yolo: true`, and follows this same state machine.

Create the card from the template, out of the roadmap or a modification, resolve epoch/phase/modification yolo inheritance, record `depends_on`, suggest S/M/L, and link relevant specs. The human owns `- [ ] Ready to plan`; an explicit command or a roadmap/modifications yolo mark may authorize the agent to check it with a log entry. WIP in 004 is at most three.

## 002 — planning

The separate planner records objective, affected areas, base strategy, fronts/dependencies, durable contracts, material risks/abort conditions, and objective criteria. No code, pseudocode, chain-of-thought, or contingent edit sequence. Research gaps become `RESEARCHES.md` prompts and block when material. Create/update canonical draft specs only for durable new promises.

- **Size is modularity, not compression.** The plan root stays ≤80 lines at **any** `size` — it is the slice everyone reads. A plan that does not fit **is sliced** into `subtasks/`, one file ≤50 lines per front that goes to a separate context; `size` grows the number of files, not the size of each. Splitting the task by `depends_on` is the exception, for fronts that share no objective. `pop_validate.py` enforces the caps.
- **The criteria are the contract.** They bind the executor and the `005_closing` gate, and must cover the card's What/Why — not only the chosen strategy. A criterion that misses the request is a plan defect, and the gate returns to 002 for it.
- **Every criterion declares who verifies it** (`verify: agent | phase | user`). **A task runs no tests at all** — every criterion that requires executing a test (unit, integration, e2e, battery) is born **`phase`**: it accumulates in the phase checklist and runs exactly once, in that phase's verification task (section "Phase verification"). `agent` is reserved for **cheap, deterministic inspection** within the agent's reach (reading an artifact, checking a section is present, a diff) — consult the scope's `notes/references/verification-limits.md` (known sandbox/infra blockers; born at the first incident). A verification that depends on infrastructure beyond that reach is born `user`: it goes to the delivery's **human verification checklist** and blocks no gate. Demanding a verification the agent cannot complete is a plan defect.
- **A `lacuna` return is an amendment, not replanning.** It appends the missing criterion and, if needed, **one** new front file — no plan rewrite. The amendment is dispatched to a **medium** planner with an amendment prompt ("append criterion X and at most one front"); a strong replanner is reserved for `premissa`. Criteria and fronts are **append-only** between rounds: renumbering breaks the `.verify.md` and telemetry references. Only `premissa` (the strategy was wrong) justifies real replanning.

## 003 — approval

Outside yolo, only `- [x] Done` advances; requested changes return to 002. In yolo, this gate **exists only for `critical: true`**: the strong Judge Dredd judges the plan in a clean session, checking verifiability, sufficient brief, safe ownership/dependencies, proportional specs/research, and absence of avoidable `(user)` work. Returns 1–2 automatically go to 002; failure 3 sets `circuit_breaker: true`, blocks, and requires human reset. A non-critical yolo task transits **002 → 004 directly, without a round** — yolo trusts the agent's plan and concentrates judgment in `005_closing`.

Only enter 004 once every `depends_on` has its ledger in `memory/<YYYY-MM-DD>/<id>.md`. There is no per-stage transitional window: a task in `005_closing` may still be awaiting the gate, and the memory is only born after it.

## 004 — implementation

Work only in the task's authorized repository/worktree; a local scope's tasks operate directly on `main`. Select:

- **direct executor** for one cohesive front and predominant skill;
- **sequential specialists** when one output feeds another;
- **parallel wave** only for logical and write/repository independence.

Complex fronts declare `owns`, `may_read`, `must_not_edit`, `depends_on`, expected input, skill, and criterion. Validate every diff with `pop_check_scope.py`, integrate centrally, then check the `agent` inspection criteria. A changed durable contract returns to 002 rather than silently rewriting the spec.

**No test runs here.** The task neither writes nor executes a suite on its own: a test criterion is `verify: phase` and runs in the phase's verification task. The task's verification is limited to the cheap-inspection `agent` criteria.

**Verification stop rule:** at most **two attempts** to make an `agent` criterion pass when the failure is environmental (sandbox, permissions, flakiness). On the second, record `ambiente` in the telemetry, reclassify the criterion as `verify: user` with a Log line and **move on** — never build new infrastructure just to verify: that is scope expansion.

**Re-entry is partial.** A task returned from the gate re-runs **only the fronts named in the delta**; an intact front stays integrated and is never re-executed or re-integrated. Validate the re-entry diff against the `owns` of the delta's fronts — touching an intact front is out-of-scope change, even when correct. **Expensive evidence is reused:** a capture matrix, a long test battery or a costly run only regenerates the slice affected by the delta — the rest stands on the previous round's stamp/hash.

## 005_closing — quality gate, delivery and close

One stage, three acts in order. **No act-3 effect happens before gate approval** where the gate exists: memory, spec sync, `close` and folder deletion all run afterwards.

**Act 1 — quality gate.** Yolo only. `pop-judge-dredd` is the single judge, in a clean session with its fixed native profile and separate from planner/executors. `size`/`critical` changes only `differential|full` depth. Contract: [[specs/judge-dredd|Judge Dredd]] — *always follow it: the invariants, powers and artifact cap live there*.

- **One judge, one artifact.** The judgment is born in `<id>.verify.md` ([[_templates/TASK-VERIFY|TASK-VERIFY]], ≤80 lines): the original request first, then criteria, specs and diff; findings with severity and evidence filtered by the skill's **materiality test**; a single verdict. A new round appends a section to the same file and **never** deletes the previous one; the highest-numbered one decides. Every round ends with the machine marker `<!-- pop-verdict round=<n> decision=aprovada|reparo-dirigido|execucao|lacuna|premissa -->` — it (not the prose) is what `pop_move`/`pop_validate` read.
- **Approval is terminal.** A round that approved ends the gate: there is no second judgment, "independent review" or addendum that reverts an approval — re-judging an approval is an orchestration bug, inflates counters, and `pop_move` refuses a return whose last `pop-verdict` is `aprovada`. Doubt about an approval belongs to the human, not to another judge.
- **He judges by reading, not by re-run.** The judge rules on the integrated diff and the recorded evidence; he does **not** re-run criteria or execute tests — testing belongs to the phase's verification task (section "Phase verification"). A `verify: phase` criterion is not judged here: the judge only checks it was recorded in the phase checklist. **Single exception — the test×code dispute:** a finding grounded in a prediction ("this test will fail against this code", a spec/test assert touched by the diff against the implementation) does not return by reading: the judge runs **only the disputed test file** and attaches the result as the finding's evidence — never the suite. A run made impossible by the environment follows the qualified-pass rule.
- **The differential round's surface is frozen in the delta.** A front approved in a previous round stays approved: an assert or test introduced by the repair itself does not invalidate it retroactively nor sustains a blocker against it — otherwise every repair manufactures the next round's rejection and the gate becomes infinite regression. A conflict between a new test and an approved implementation is a defect **of the delta** (directed repair on the test or on the exact spot) or a follow-up; only `premissa` invalidates what was already verified.
- Read in this order: objective, specs/contracts and diff; the execution report is support, not truth. First answer whether the **original request** — the card's What/Why — was met, before the plan's criteria. Choose `differential` or `full` and record reason/surface: **a previous return does not imply full review** — only `premissa` invalidates what was already verified, and `full` is reserved for it and for `critical: true`; after `lacuna` or an execution failure the differential covers the **delta** (the criteria and fronts that re-entered) and audits the rest by evidence. Review behavior, edges, complexity, coupling, naming, errors, security, docs, and the specs/DOX touched; in code, follow `clean-code-review`. Every finding carries excerpt/evidence, impact and severity (**blocking**, **suggestion** or **nit**), and there is exactly one judge per round.
- **Transition — the adversarial gate was retired on 2026-08-04.** A card whose `created:` predates that date may carry `.defense.md`, `.r<n>.accusation.md` and `.r<n>.judgment.md` as history; its pending judgment already runs with the Judge Dredd, who treats those artifacts as evidence. A card created on or after the cutoff produces none of the three. Only `created:` (immutable) counts; no new field.
- **An environment failure never returns.** A criterion blocked by sandbox/infra or non-deterministic (flaky) evidence gets a **qualified pass** with whatever alternative evidence is available and joins the delivery's human verification checklist; a return demands a reproducible product defect.
- **Directed repair — a pinpoint defect does not pay for a round.** An execution blocker whose delta is pinpoint — named `file:line`, objective remedy, no strategy change — has directed repair as the **default route, not an option**: the judge declares `pontual=true` in the delta, the orchestrator dispatches a **medium** executor with only the delta, and whoever judged checks the repair **in the same round**, in a ≤10-line addendum to its artifact (within the round's cap), re-running only the delta's items. It consumes no counter and the folder does not move — `pop_move` **refuses** the full route for a `pontual=true` delta. The full route stays for diffuse defects, `lacuna` and `premissa`; at most **two** directed repairs per round — a third proves the defect was not pinpoint: the judge reclassifies the delta as diffuse and only then the full route holds (`--force` with the reason, if the previous delta still says pinpoint).
- **The gate does not expand the scope.** A real finding outside the card's What/Why becomes a traceable follow-up (a proposed task/modification, or a memory record), never a new criterion or front of this task. A `lacuna` return fits **once** per task: the second genuine gap closes the task with what the request covered, and the rest is born as its own task.
- **Three exits:** approved → act 2; **execution blocker** → 004 (the executor did not meet the contract); **plan defect** → 002 (the contract did not cover the request, and the executor delivered what it was given). Each route has its own counter: execution counts in `yolo_005_returns`, plan defect in `yolo_003_returns`. Two returns per counter re-enter automatically; the 3rd opens `circuit_breaker`. **Progress breaker:** a return whose delta repeats the previous one's theme with no new fact does not re-enter — it opens the circuit breaker early; iterating without progress is the waste it exists to cut.
- **Every return carries a named delta**, without exception: type (`lacuna` | `premissa` | `execucao`), affected criteria, affected fronts, and the fronts that stay intact. The delta is what makes a return cost the size of the defect instead of a whole cycle — without it, 002 cannot tell amendment from replanning and 004 does not know what to re-run. Beyond the prose, the delta gets the machine marker `<!-- pop-delta round=<n> kind=<type> pontual=true|false paths=<comma,separated,files> frentes=<Fxx,...> intactas=<Fxx,...> -->` in the same round: `pop_move` refuses a return without a coherent verdict/delta, and the `004→005_closing` reentry only passes if the diff since `return_base` (written to the card by `pop_move` itself) touches some `paths` of the delta — re-presenting the same problem to the judge is refused at the source. The reentry executor's prompt is born from the marker, verbatim — immune to the orchestrator's context compaction. The type is written to `return_kind:` by `python3 pop/scripts/pop_move.py … --return-kind <type>`, the field's only writer, which fails closed on `005_closing→002`; agents never edit it (nor `return_base:`) by hand. Outside yolo, the human records the same delta in the `.approval.md` merge round when asking for a PR fix.
- **The gate does not fix what it rejected.** Naming the delta is the limit of its power: a judge that dispatches the correction ends up judging work it commissioned, and the independence that makes the gate worth anything disappears.
- **Non-yolo — no agentic reviewer.** The gate is the **human PR** of act 2, and the objective criteria already ran in 004 (inspection criteria + `pop_check_scope.py`). With no PR — a local scope — there is no verification gate at all: the stage goes straight to act 3. The proof lives in `main` and in the memory.

**Act 2 — integration and PR.** A local scope is already on `main`, with no task branch/worktree/PR. External **non-yolo** scope: open the task PR, set `pr` and `awaiting_merge: true`, and wait for the human merge. External **yolo** scope: run `pop_delivery.py integrate <id>` mechanically into the current working branch, no PR per task; conflicts/dirty state/missing branches block. Every PR carries a **Human verification** section: the accumulated `verify: user` criteria (including the ones reclassified as `ambiente`), each with the manual step and the expected pass; with no PR (local scope), the checklist goes into the final approval round/open question — the human is the verifier of last resort for these items.

**Act 3 — close-out.** Idempotent: validate state before each effect, skip what is already done, and abort preserving card/roadmap on technical failure.

1. Write the task memory under `memory/<YYYY-MM-DD>/`, where the folder is the completion date (equal to `finished`): the **ledger** `<id>.md` ([[_templates/MEMORY|MEMORY]], ≤1200 chars) with identity, dates, commit, explicit `pr`, delivery, verification, contract impact and the index of the entries; and one **entry** `<id>.<nn>-<slug>.md` ([[_templates/MEMORY-ENTRY|MEMORY-ENTRY]], ≤800 chars) per thing done — changed areas, telemetry, every durable decision, every deviation — numbered in chronological order and each carrying **at least one evidence wikilink** (the spec changed, the file touched). An entry the ledger does not index is orphaned; invalid memory aborts the close. In yolo, the Judge Dredd who approved writes it, in the same session — he has just read the diff.
2. Synchronize only the specs/DOX actually affected, plus phase/epoch/modification/index statuses.
3. Run `python3 pop/scripts/pop_roadmap.py close <id>`; it requires the card in `005_closing` plus valid memory and removes exactly one task row while preserving epoch/phase/modification/open tasks.
4. Extract only reusable learning; remove external task worktrees/ephemeral branches.
   - **Harvesting the judgment.** A decision **contested and upheld** in the `.verify.md` becomes a durable record only when **all three** tests pass: ruled on the merits · **recurrence** (the rationale would decide a future task that knows nothing of this one; if it falls together with this diff, it is circumstance) · **novel** in any live spec or note (if one already exists and diverges, fix the existing one instead of creating another). Destination: a durable contract, invariant or interface → a line in a spec; the reason behind a choice → a note in `notes/decisions/`. **The default is not to record:** if a test fails, the decision dies in the task memory, whose entries already carry decisions/deviations — and a judgment with no harvest generates **no** "no harvest" record.
5. At the final external yolo task of the marked scope — single task, phase/epoch or modification — **suggest to the human** the PR from the current working branch to `main`, with the scope's human verification checklist for the PR body; the agent never opens a PR on its own and creates it (`pop_delivery.py scope-pr`, then sets `pr`/`awaiting_merge`) only on the user's explicit request. The merge is always human. A local scope opens no task/scope PR.
6. Delete `kanban/005_closing/<id>/` only after every prior effect succeeds; memory + Git keep the durable proof.

## Phase verification — where tests run

Tests do not run per task: **they run once per phase**, concentrated in its last task. This is the rule that makes the flow cheap — an ordinary task delivers and is judged by reading; the suite is paid for exactly once.

- **Every roadmap phase ends with a verification task** (slug `phase-verification`, last in the table, `depends_on` all the others): `plan-roadmap` proposes it and `new-task` materializes it like any task. Its 002 receives the **phase checklist** — every `verify: phase` criterion accumulated by the previous tasks (the source is the memory and the plans archived in Git).
- **Scope of the verification task:** write/update the suite that covers the checklist, run it and **fix what it catches** — the originating tasks have already closed and their folders were deleted, so an execution defect revealed here is a fix inside this task, not a return to those. Its Judge Dredd gate **may** demand a re-run: it is the only task in which a test is an `agent` criterion.
- **A defect above the phase's reach** (a wrong durable contract, a previous task's request structurally unmet) is not fixed here: it becomes a proposed modification or new task, with the finding recorded in the memory.
- **The phase only completes with the verification task approved.** Modification tasks belong to no phase: their criteria stay `agent` (inspection) or `user`, and an indispensable test in them uses cheap deterministic verification declared in the plan.

## Yolo scheduling, telemetry, and circuit breaker

- A yolo mark may come from the roadmap/modifications or from the human saying “start the flow in yolo”. With no card, `new-task` materializes and releases it while recording the conversational source; yolo is never a waiver. **Asking for yolo implies the kanban:** the agent warns ("this goes through the kanban") and materializes the task; the no-kanban route has no yolo mode.
- `yolo: true` keeps the same state machine with a **single quality gate in `005_closing`**, judged by `pop-judge-dredd` in a clean session with its fixed native profile. It first checks the original request, then plan, specs, diff and quality—by reading, without rerun. Outside yolo the gate is the human PR. `critical: true` keeps 003 with the same role/profile and makes 005 `full`.
- **Two returns per route, always with a delta:** an execution blocker returns to 004 (`yolo_005_returns`, type `execucao`); a plan defect returns to 002 (`yolo_003_returns`, type `lacuna` or `premissa`). The 3rd failure of the same route opens the circuit breaker. Only the delta's fronts re-enter. **One judge per round and approval is terminal:** an `aprovada` verdict ends the gate — no second judgment; a `pontual=true` delta follows directed repair, with no `pop_move` and no counter. The locks are mechanical: `pop_move` validates the `.verify.md`'s `pop-verdict`/`pop-delta` markers and refuses a reentry with no work on the delta's `paths`; the gate's wall-clock budget (below) cuts the cycle that does not converge.
- `pop_yolo.py wave` selects up to three eligible tasks with satisfied dependencies and isolated projects by default; overlap serializes.
- Collect every stage context before transition; never end with a stage agent running or merely promise agent-owned continuation.
- Minimal telemetry stores stage, context count/IDs, return counters, verification strategy/tests, duration, and result. Never store prompts, chain-of-thought, or discarded attempts. **Watchdog:** a task in 004 with no commit, ref or new Log line for more than ~2h is an anomaly — the orchestrator sets `blocked_reason` or justifies it in the Log; a silent dead window is an orchestration bug (`pop_status.py` reports it).
- **The gate's wall-clock budget (yolo):** a task's `005_closing` + repairs cycle has a wall-clock cap per `size` — **S ~1h, M ~2h, L/critical ~3h**, measured from the first entry into `005_closing` (telemetry/Log timestamps). Blown without an approval → the orchestrator does **not** launch another round: it records `blocked: true` with a diagnosis (what each round returned and why progress stopped) and hands it back to the human. Constant activity that does not converge is as anomalous as a dead window.
- `pop_yolo.py reset <id> --gate 003|005 --reason ...` is explicit human intervention and clears only that gate's counter/block.
- The judge judges; the orchestrator moves, integrates, opens PRs, and closes. No agent merges a human-owned PR.

## Transversal rules

- Claim first; a live claim by another agent makes the task folder read-only.
- Dependencies must be completed before consumers; never implement missing work opportunistically.
- Every internal wikilink carries a trigger. Dates use `YYYY-MM-DD`; notes stay near 150 lines, the plan root ≤80 and each front file ≤50.
- **A return is incremental:** every return leaving `005_closing` names a delta and is classified in `return_kind`; the re-entry works only on the delta and the re-review is differential over it. A return that discards approved work is an orchestrator bug. Normal returns: 003→002, 004→002, `005_closing`→004 (execution blocker) and `005_closing`→002 (plan defect).
- **An explicit human command overrides only its stated scope:** obey without reinterpreting what it actually superseded, and record the deviation. “Apply”, “execute”, “urgent” and “finish it” do not decide the triage for you. **The kanban is optional** (rule 13 of [[AGENTS|AGENTS]]): “in yolo” or a roadmap/modifications item implies the kanban by default — warn and proceed — and the no-kanban route never waives memory, specs or the project's skills.
- **No work outside a route:** project content changes in 004 (after 003 or through the legitimate 002→004 transition for non-critical yolo, in the correct worktree), through the direct-fix route approved by the rule-13 triage **or through the no-kanban route (plan mode) chosen by the user in the triage**. A request the triage sends to the kanban runs `new-task` → `advance-task`; do not improvise.

### Direct fix — the route without a card

The rule-13 triage in [[AGENTS|AGENTS]] decides at the entrance. Direct fix when **all** hold: the scope is evident from the request itself; no new durable contract; no planning interview needed; it fits in one session. Any "no" — or a doubt one one-line question cannot settle — becomes a task.

1. Execute through the scope's delivery route (local: straight to `main`; versioned: short branch + PR, like any delivery).
2. Verify with the aggregate gate/deterministic tests — no agentic reviewer. A criterion the agent cannot verify goes to the human verification checklist (PR or INBOX).
3. Durable proof: ledger `memory/<YYYY-MM-DD>/F-YYYYMMDD-<slug>.md` ([[_templates/MEMORY|MEMORY]], `authorization: direct-fix triage`) + one entry per thing done, and sync of the affected specs/DOX. **No line in the roadmap or MODIFICATIONS** — the record is memory + specs.
4. Grew midway (second objective, durable contract touched)? **Stop**: materialize the task and report what was already done in the card.

### No-kanban route — the coding agent's plan mode

The kanban is **optional**: the agent recommends it when the change is large, and it is the implied default (with a notice to the user) when the request is yolo or covers a roadmap/modifications item. When the user opts out of the kanban, the route is **the coding agent's own plan mode** — planning and approval happen there, with no card, stages or `pop_move`. The route waives ceremony, **never continuity**:

1. Before writing, record the request and the choice in the ledger `memory/<YYYY-MM-DD>/D-YYYYMMDD-<slug>.md`, using [[_templates/MEMORY|MEMORY]]; the `D-` ID identifies work without a card and fills `authorization`.
2. Plan in the coding agent's plan mode and only execute with the plan approved; delivery follows the scope's route (local: straight to `main`; versioned: short branch + PR, like any delivery).
3. **The project's agents and skills keep applying:** delegation-first, the six specialists, `clean-code-*`, `ui-*` and the other applicable skills — the route changes the tracking, not the standard of work.
4. Before finishing, complete the ledger with commit/PR, result and verification, open one entry per thing done and record the specs and DOX impact assessment, updating only the contracts actually affected.
5. Without a route to that durable evidence, do not edit. If the work grows beyond the approved plan (second objective, new durable contract), **stop** and return to triage.
6. The no-kanban route **has no yolo mode**: without a card there is no `pop-judge-dredd`, circuit breaker or gates — the human approves the plan and the result.
