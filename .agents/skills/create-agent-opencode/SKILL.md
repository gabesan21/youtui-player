---
name: create-agent-opencode
description: Generate and locally validate candidate bundles for PoP's six OpenCode subagents from `.agents/agents/`, without invoking models.
---

# Create OpenCode agents

Treat `.agents/agents/*.md` as the authoring source and generated bundles as disposable projections.

## Workflow

1. Read all six specialists and [[.agents/skills/create-agent-generic/SKILL|create-agent-generic]] in full. The main session follows `AGENTS.md` and is not materialized.
2. Use a closed profile like `fixtures/profiles.valid.json`: capabilities declare variants and every role fixes `mode`, `model`, `variant`, permissions, and skills.
3. Build in an empty candidate root, then validate static bytes, schema, profile, permissions, manifest, complete bodies, and `subagent_depth`.
4. Materialize only the validated generated files; never hand-edit a generated bundle.

OpenCode splits the model ID at the first `/`. Kimi subscription models therefore use `kimi-for-coding/<model>`; OpenRouter models use `openrouter/<organization>/<model>`. Never omit the OpenCode provider prefix.

## Fail-closed invariants

- Every role is `subagent`; the native main agent follows `AGENTS.md`.
- Emit `subagent_depth: 2`; only planner and execution coordinator receive exact child allowlists.
- Use `permission`, not deprecated `tools`; deny web and external directories and default-deny Task/skill.
- Do not enable background agents, experimental flags, concurrency promises, or Pi compatibility.
- Do not invoke `opencode`, a model, session, provider, auth, network, discovery, or diagnostics.

The declared profiles are: planner/Judge `kimi-for-coding/k3-256k` high; recon `openrouter/qwen/qwen3.5-flash-02-23`; executor `openrouter/qwen/qwen3-coder-next`; execution coordinator and phase verifier `openrouter/deepseek/deepseek-v4-pro` high.

Return `BLOCKED` if a capability, source, or deny cannot be represented. Completion ends at deterministic generation, hashes, declared policies, and safe local writes.
