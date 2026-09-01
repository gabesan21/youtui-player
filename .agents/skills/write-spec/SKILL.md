---
name: write-spec
description: Standardizes spec creation for any kind of project (software, writing, business, research...), guiding the user with the right questions for the type. Use when creating or rewriting a spec.
---

# write-spec

A spec records a **durable contract**, not the contingent implementation chosen for one task. Prefer behavior, invariants, promised interfaces, errors/limits and objective conformance criteria. Do not persist chain-of-thought, pseudocode, edit sequences or speculative snippets.

Creates a spec in `pop/specs/` (a scope whose harness lives at its own root: the same paths, without the `pop/` prefix) from `_templates/SPEC.md`, interviewing the user with the right questions for the project type. A spec answers **one** question; if it starts answering two, it is two specs.

**Delegate to subagents:** almost nothing — it is an interview; broad reading of existing material to ground the spec goes to a subagent with a specific question and an answer ≤30 lines.

## Procedure

1. **Scope the topic:** confirm with the user in one sentence what the spec covers — and what stays out ("Out of scope" section).
2. **Interview by type** (2–3 questions at a time; adapt for unlisted types):
   - **Software:** expected behavior, data involved, error cases, integrations, what "done" means.
   - **Writing:** target audience, tone, structure/sections, sources, target length, quality criterion.
   - **Business/process:** steps, owners, inputs/outputs, success metrics, risks.
   - **Research:** questions to answer, method, acceptable sources, sufficiency criterion (when to stop).
   - **Personal/habit:** desired outcome, triggers, frequency, how to measure progress.
3. **Write verifiable requirements:** each requirement must make it possible to answer "is this true?" with yes/no. "Good text" is not a requirement; "each chapter ≤3,000 words with a narrative opening" is.
4. **Uncertainties don't block:** what the user doesn't know goes to the "Open" section — the spec is born as `draft` and evolves.
5. **Link:** roadmap phase, related tasks, other specs. File name in kebab-case.
6. **Stop at the contract:** record behavior, invariants, interfaces, errors and conformance. Change strategy stays in the plan; reusable procedure in a skill; code appears only when it is itself the promised interface.

## Lifecycle (see the `sync-specs` skill)

`draft` → `approved` (together with the 003 gate of the first task that implements it, or direct user approval) → `implemented` (when reality matches the spec) → `obsolete` (with a link to the replacement).

## Cautions

- ≤150 lines; if it grows, extract auxiliary specs and link them.
- An explicit out-of-scope keeps the spec from bloating later.
- Do not anticipate classes, functions, layers or implementation order the contract does not require.
- Never leave a `<...>` placeholder behind.
