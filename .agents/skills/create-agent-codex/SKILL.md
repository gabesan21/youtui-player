---
name: create-agent-codex
description: Generate and locally validate native Codex custom agents from canonical `.agents/agents/` contracts without executing a model or contacting a provider.
---

# Create Codex agents

Project a canonical role into standalone TOML without changing its semantics. `pop/scripts/build_agent.py` makes rendering, static validation, collision handling, and promotion reproducible.

## Workflow

1. Read `.agents/agents/<role>.md` and triggered sources in full.
2. Choose only values permitted by `references/config-contract.md`.
3. Render outside `.codex/agents/`, validate locally, then promote atomically:

```bash
python3 .agents/skills/create-agent-codex/pop/scripts/build_agent.py render \
  .agents/agents/pop-executor.md /tmp/pop-executor.toml \
  --model gpt-5.6-terra --effort medium --sandbox-mode workspace-write
python3 .agents/skills/create-agent-codex/pop/scripts/build_agent.py validate-static \
  /tmp/pop-executor.toml --source .agents/agents/pop-executor.md
python3 .agents/skills/create-agent-codex/pop/scripts/build_agent.py promote \
  /tmp/pop-executor.toml .codex/agents/pop-executor.toml \
  --source .agents/agents/pop-executor.md
```

Use `--replace` only to replace a valid destination for the same role. Never replace malformed or foreign collisions. The final filename must match `name` and live under `.codex/agents/`.

`developer_instructions` preserves the complete canonical body. Sandbox mode does not enforce path ownership or tool denies and never replaces those obligations.

Completion reports source/candidate/destination, model-effort-sandbox tuple, digest, and `completed`. Remote availability, model behavior, spawn behavior, auth, network, and providers are outside this local harness contract.
