---
name: create-agent-generic
description: Create, review, or update the agent-agnostic semantic definitions of PoP's six specialists and guide future builders without imposing a runtime schema.
---

# Create generic agents

Keep one authoring source per role in `.agents/agents/`. These Markdown files are semantic contracts; generated artifacts are disposable projections and never become the source.

## Workflow

1. Identify the requested roles and read every corresponding body in `.agents/agents/` in full.
2. Read sources referenced by a body only when the reference trigger applies.
3. Preserve identity, trigger, path-based acquisition, permissions, input/output, termination, ownership, dependencies, gates/re-entry, and denies.
4. Require the role to acquire content directly from authorized paths; never accept a substantive summary instead of the source.
5. Keep bodies tool-independent. Destination-specific decisions belong to the consuming builder.
6. Inspect all six bodies and report changed paths plus a short coverage matrix.

## Canonical sources

- [[.agents/agents/pop-planner|pop-planner]] — read when creating or translating the 002 planner.
- [[.agents/agents/pop-recon|pop-recon]] — read when creating or translating delegated reconnaissance.
- [[.agents/agents/pop-execution-orchestrator|pop-execution-orchestrator]] — read for the 004 front coordinator.
- [[.agents/agents/pop-executor|pop-executor]] — read for the 004 front executor.
- [[.agents/agents/pop-judge-dredd|pop-judge-dredd]] — read for the yolo-gate judge.
- [[.agents/agents/pop-phase-verifier|pop-phase-verifier]] — read for the phase-final verifier.

Do not copy the bodies into this skill, `references/`, or `assets/`.

## Create or update

Create one file per specialist with the canonical name and nine explicit sections. The main agent is not materialized: it follows `AGENTS.md`, delegates first, and retains routing, integration, and transitions. Reject changes that collapse separation between planning, execution, judgment, and integration.

## Consume in a builder

Read the selected role in full and map every obligation to official destination features. Preserve powers and denies, produce a self-contained artifact, and record capabilities with no equivalent. Never weaken the source to fit a runtime limitation; return `BLOCKED` when that limitation changes semantics.

## Evidence and stop

Finish `completed` with path evidence only when every mandatory topic is covered and no deny was weakened. Finish `BLOCKED` when a source/dependency is absent, semantics are incompatible, or authorization would need broader reading, writing, or powers.
