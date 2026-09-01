---
name: run-opencode
description: Invokes opencode as a headless executor of coding tasks (opencode run, yolo mode, custom agents, multi-provider, NDJSON output). Use when delegating coding work to opencode via CLI - general contract and tool choice in the delegate-coding skill.
---

# run-opencode

Contract, yolo/auth rules and checklist: skill `delegate-coding` — read it before the first delegation. Before the first invocation on the machine, confirm the flags with `opencode run --help` — versions diverge (the source is from mid-2026; flags below checked against the local installation on 2026-07-12, divergences noted in each section).

## Headless invocation

```bash
timeout 600 opencode run --auto --format json "scoped task"
```

- `opencode run [message..]` processes, prints and exits (without arguments it opens the TUI — never call bare `opencode` in automation).
- **stdin is not guaranteed** ("if supported" in the source) — pass the message as an argument.
- Repeated invocations: start `opencode serve` once and use `--attach http://localhost:<port>` to avoid cold start.

## Output and parsing

- `--format default|json`. The json is **NDJSON** (one event per line): `step_start`, `text`, `tool_use`, `tool_result`, `step_finish` (carries tokens and cost), with `sessionID` in the events.

```bash
opencode run --format json "..." | jq -r 'select(.type=="text") | .part.text'      # final text
opencode run --format json "..." | jq 'select(.type=="step_finish") | .part'       # tokens/cost
```

## Sessions

- Continue the previous one: `-c/--continue`; resume a specific one: `-s/--session ses_...`; branch preserving the original: `--fork`; name: `--title "..."`.
- Management: `opencode session list --format json -n 10`, `opencode export <ID>`, `opencode import <file|URL>`.
- Capture the `sessionID` from the NDJSON events for follow-up.

## Yolo mode

Yolo is this skill family's default mode (decision of 2026-07-12); control comes from the orchestrator (isolated worktree, scoped prompt, timeout). **The flag varies by version:** on the local installation the flag is `--auto` ("auto-approve permissions that are not explicitly denied"); the source documents `--dangerously-skip-permissions` — use whatever `opencode run --help` shows. A quirk in both: **an explicit `deny` in `opencode.json` still wins** — if something is blocked inexplicably, look for a `deny` in the repo's config. Fine-grained permissioning (`permission` allow/ask/deny, `OPENCODE_PERMISSION`) exists, but is **not used** here.

## Specific agents

- Built-in primaries: `build` (full dev, default) and `plan` (read-only). Subagents: `general`, `explore`, `scout`.
- Selection: `--agent <name>`; subagents also via `@mention` in the prompt.
- Custom: `opencode agent create` (or non-interactive with `--path --description --mode --tools --model`), or markdown with frontmatter (`description`, `mode: primary|subagent|all`, `tools:`) in `.opencode/`.

## Model

- `--model/-m provider/model` — multi-provider is the strong point: `anthropic/claude-sonnet-4-6`, `openai/gpt-5`, `google/gemini-3-pro`...
- `--variant` controls reasoning effort (Anthropic: `high`/`max`; OpenAI: `none`…`xhigh`; Google: `low`/`high`).
- `opencode models [provider]` lists; persistent config in `opencode.json` (`model`, `small_model`).

## MCP

The source only documents MCP **permissions** (`"mymcp_*"` patterns in the `permission` block), not server registration — check the official docs if you need MCP.

## Context and directories

- `--dir <path>` sets the run's working directory.
- `--file/-f <path>` (repeatable) attaches files to the prompt.
- Inline config without touching files: `OPENCODE_CONFIG_CONTENT='{"model":"..."}'` (priority: env → local `opencode.json` → global) — useful for the orchestrator to inject config per invocation.

## Auth

Precondition: already logged in (`opencode auth login` already done by the human; credentials in `~/.local/share/opencode/auth.json` or `ANTHROPIC_API_KEY`/`OPENAI_API_KEY` in the environment). **Do not configure login in this skill.** If the output mentions credential/API key/provider auth/401: **abort the orchestrator's entire task** — no retry, no fallback; an immediate failure with **no** auth signal is an invocation error, not a login one (rule 2 of `delegate-coding`).

## Gotchas

- The `question` tool can hang without a TTY — the prompt must give all the information and forbid questions.
- `websearch` requires the OpenCode provider or `OPENCODE_ENABLE_EXA=true`; `lsp` requires `OPENCODE_EXPERIMENTAL_LSP_TOOL=true`.
- `read` caps at 2000 lines per call (offset/limit for large files).
- Bash rules in the config: the **last** match wins — a residual `deny` may come from there.

## Recipes

```bash
# Editing task with an explicit model
timeout 600 opencode run --auto --format json \
  --model anthropic/claude-sonnet-4-6 "Write tests for src/utils.ts; run them"

# In an isolated directory, cheap model, cost captured
timeout 600 opencode run --auto --dir /path/worktree \
  --model anthropic/claude-haiku-4-5 --format json "Execute npm test and report results" \
  | jq 'select(.type=="step_finish") | .part'

# Recon with the plan agent (read-only by nature)
timeout 300 opencode run --agent plan --format json "Audit the codebase for security issues"

# Follow-up in a fork of the session
opencode run --session ses_abc123 --fork --auto --format json "Try an alternative approach"
```

## See also

- Contract and choice: `delegate-coding` · Same operation in another tool: `run-cursor-agent`, `run-codex`.
