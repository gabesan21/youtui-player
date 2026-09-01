---
name: create-agent-kimi-code
description: Project one of PoP's six specialists into Kimi Code agent Markdown and candidate configuration, with symbolic primary/secondary routing and fail-closed local validation.
---

# Create Kimi Code agents

Treat `.agents/agents/<role>.md` as the authoring source and preserve its complete body.

## Format limits

- Use only `name`, `description`, `whenToUse`, `override`, `model_preference`, `tools`, `disallowedTools`, and `subagents`.
- `primary` resolves to the current main model. `secondary` resolves through `[secondary_model]`, fixed here to `kimi-code/kimi-for-coding` (K2.7); never write the concrete alias in an agent.
- Do not promise effective model+effort per spawn, maximum nesting, or aggregate runtime validation.
- Do not label K2.7 as medium effort: its boolean Thinking does not prove that level.
- Parse candidate TOML with `tomllib`; never invoke Kimi Code.

## Workflow

Read the canonical role and [[.agents/skills/create-agent-generic/SKILL|create-agent-generic]] in full. Use `build` to preserve the body, apply conservative tool/child allowlists, and optionally create a candidate config. Use `validate` against the source, generated agent, routing, and candidate config.

Planner and Judge use `primary`; recon, execution coordinator, executor, and phase verifier use `secondary`. The materialized `.kimi-code/config.toml` contains K3 primary and K2.7 secondary with no credentials and no artificial secondary effort.

Generation and validation must not invoke `kimi`, a model, provider, auth, network, discovery, or diagnostics. Finish `BLOCKED` when a required guarantee or deny cannot be represented.

## Sources

- [[specs/multi-agent-orchestration|Multi-agent orchestration]] — *follow to preserve roles, envelopes, ownership, gates, and local-delivery boundaries*.
