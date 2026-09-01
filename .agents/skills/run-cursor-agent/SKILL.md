---
name: run-cursor-agent
description: Invokes the Cursor CLI (cursor-agent) as a headless executor of coding tasks (-p --force, sessions by UUID, models, JSON output). Use when delegating coding work to Cursor via CLI - general contract and tool choice in the delegate-coding skill.
---

# run-cursor-agent

Contract, yolo/auth rules and checklist: skill `delegate-coding` — read it before the first delegation. Before the first invocation on the machine, confirm the flags with `cursor-agent --help` — versions diverge (the source is from mid-2026).

## Headless invocation

```bash
timeout 600 cursor-agent -p --force --output-format json "scoped task"
```

- `-p`/`--print`: headless mode. The prompt is a positional argument and comes **after** the flags.
- Without `--force` the agent is read-only; `--force` (alias `--yolo`) unlocks edits and commands.
- Accepts pipe: `git diff | cursor-agent -p "review this diff"`.
- Reference files directly in the prompt (relative/absolute paths; images included).

## Output and parsing

- `--output-format text|json|stream-json`. The JSON carries `result`, `files_modified`, `summary`.
- `stream-json` is NDJSON of events (`system`, `assistant`, `tool_call`, `tool_result`, `result`, `error`); add `--stream-partial-output` for text deltas. Also useful for detecting completion when the process hangs (see Gotchas).

```bash
cursor-agent -p --force --output-format json "..." | jq -r '.result, .summary'
```

## Sessions

- `cursor-agent ls` lists; `cursor-agent resume` resumes the last one; `--resume <uuid>` resumes a specific one; `--continue` continues the previous one.
- `create-chat` creates an empty session and returns the ID.
- **`-n/--name` is only a display label — resuming requires the UUID.** Capture the id at creation.
- `--cloud`/`-c` hands off to the cloud (continues after closing the terminal).
- Best practice from the source: one task = one session; prefer discrete prompts over one long `--continue`.

## Yolo mode

`--force` — it is this skill family's default mode (decision of 2026-07-12); control comes from the orchestrator (isolated worktree, scoped prompt, timeout). With MCP, add `--trust --approve-mcps`. `--sandbox enabled|disabled` exists, but `.cursor/sandbox.json` is ignored in headless (bug in the source) — don't rely on it.

## Specific agents

- Execution modes: `--mode agent|plan|ask` (`plan` = read-only, `ask` = Q&A without edits) — no normal use here, given the yolo contract, but useful for recon.
- Project rules: `.cursor/rules/` (create with `cursor-agent generate-rule`); there is no dedicated system prompt flag — context goes in the prompt or in the rules.
- Subagents **do not inherit the model** and fall back to `composer-1.5` — no reliable fix; avoid relying on them.

## Model

- `--model/-m <id>`; list with `cursor-agent models` or `--list-models`.
- **`--model default`/`auto` fails on some plans — always specify** (e.g. `composer-2`, `claude-sonnet-4.6`, `gpt-5.4-low`, `gemini-3.1-pro`).

## MCP

- Config in `.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (global), `mcpServers` block with `command/args/env`; interpolation `${env:NAME}`, `${workspaceFolder}` etc.
- In headless/CI, MCP is only recognized with `--trust --approve-mcps`.
- `cursor-agent mcp list`, `mcp list-tools <id>`, `mcp enable/disable <id>`.

## Context and directories

- `--workspace <dir>` sets the working directory.
- Ready-made isolated git worktree via flag: `-w/--worktree "name"` + `--worktree-base <branch>` (`--skip-worktree-setup` skips the `.cursor/worktrees.json`).
- Context quality drops near 80-90% of capacity — scoped prompts, not a repository dump.

## Auth

Precondition: already logged in (or `CURSOR_API_KEY` in the environment). **Do not configure login in this skill.** If the output mentions credential/API key/login/401: **abort the orchestrator's entire task** — no retry, no fallback; an immediate failure with **no** auth signal is an invocation error, not a login one (rule 2 of `delegate-coding`).

## Gotchas

- **It may hang without exiting when done** — `timeout <s>` is mandatory in every invocation; to monitor, use `stream-json` and detect the `result` event.
- MCP "not configured" in CI → missing `--trust --approve-mcps`.
- A session name doesn't resume; only the UUID.
- Subagents degrade to `composer-1.5`.

## Recipes

```bash
# Direct editing with JSON output
timeout 600 cursor-agent -p --force --output-format json --model composer-2 \
  "Add tests for src/utils.ts; run them; don't touch other modules"

# Stream to track progress and detect completion
timeout 900 cursor-agent -p --force --output-format stream-json --stream-partial-output \
  "Analyze the project and generate a report in REPORT.md"

# In its own isolated worktree
timeout 900 cursor-agent -p --force -w "task-fix-login" --worktree-base main \
  --model claude-sonnet-4.6 "Fix bug X in src/login.ts"

# With MCP (Playwright etc.)
timeout 900 cursor-agent -p --force --trust --approve-mcps "Run the E2E tests with Playwright and summarize failures"
```

## See also

- Contract and choice: `delegate-coding` · Same operation in another tool: `run-opencode`, `run-codex`.
