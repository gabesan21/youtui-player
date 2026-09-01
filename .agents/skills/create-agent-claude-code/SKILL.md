---
name: create-agent-claude-code
description: Generate, update, and validate PoP's six Claude Code specialists from `.agents/agents/` and explicit profiles. The main agent follows AGENTS.md and is not a custom agent.
---

# Create Claude Code agents

Treat `.agents/agents/*.md` as the sole semantic source. Generate a self-contained projection: native frontmatter followed by the complete canonical body.

## Profile

1. Use JSON `version: 1` with exactly the six canonical specialists under `roles`.
2. Declare `model`, `effort`, `tools`, `disallowedTools`, `permissionMode`, `skills`, `nesting`, and `web` for each role.
3. Use an explicit non-`inherit` model and effort in `low|medium|high|xhigh|max`.
4. Keep `web: false`, deny `WebFetch`/`WebSearch`, and set `nesting: false` for every specialist. The native main session dispatches them according to `AGENTS.md`.

## Generate and validate

```bash
python3 .agents/skills/create-agent-claude-code/pop/scripts/build_agents.py generate \
  --source-dir .agents/agents --profiles .claude/pop-agent-profiles.json \
  --destination .claude/agents --runtime .claude/pop-agent-runtime.json
python3 .agents/skills/create-agent-claude-code/pop/scripts/build_agents.py validate \
  --source-dir .agents/agents --profiles .claude/pop-agent-profiles.json \
  --destination .claude/agents --runtime .claude/pop-agent-runtime.json
```

The builder never invokes `claude`, even for discovery or diagnostics. It validates parser, profile, hashes, deterministic bytes, collision safety, and known runtime overrides, and writes transactionally with rollback.

The optional runtime JSON accepts only `invocationModels`, `availableModels`, `parentPermissionMode`, and `thinkingEnabled`. Environment, invocation, and parent permission mode may override an agent; thinking is inherited and is never emitted in frontmatter.

## Fail closed

- Never claim frontmatter beats environment, invocation, model availability, or the parent's mode.
- Never claim reliable nested-child allowlists; all specialists have nesting disabled.
- Never edit `.agents/agents/` through this builder.
- Never execute Claude Code, a model, authentication, network, or provider calls.

Completion requires six files, a manifest, successful validation, and a second generation with identical bytes. Any unrepresentable deny returns `BLOCKED`.
