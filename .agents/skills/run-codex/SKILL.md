---
name: run-codex
description: Invokes OpenAI's Codex CLI as a headless executor of coding tasks (codex exec, yolo mode, sessions, JSONL output). Use when delegating coding work to Codex via CLI - general contract and tool choice in the delegate-coding skill.
---

# run-codex

Contract, yolo/auth rules and checklist: skill `delegate-coding` — read it before the first delegation. Before the first invocation on the machine, confirm the flags with `codex exec --help` — versions diverge (the source has references up to 2026-04; several modes are version-gated).

## Headless invocation

```bash
timeout 600 codex exec --dangerously-bypass-approvals-and-sandbox --json "scoped task"
```

- `codex exec` (alias `codex e`) runs without the TUI until completion and exits with a status code — never call bare `codex` in automation.
- Prompt as a positional argument; piped content becomes **additional context** to the argument; `-` forces reading the prompt from stdin.
- Progress goes to **stderr**, the final answer to **stdout** — redirect each one to its destination.
- Requires a git repo in the directory; outside a repo, add `--skip-git-repo-check`.

## Output and parsing

- `--json` emits JSONL (one event per line): `thread.started` (carries `thread_id`), `turn.started`, `item.*`, `turn.completed` (carries `usage` with tokens), `error`.
- `--output-schema <file.json>` validates the final answer against a JSON Schema — use it when the orchestrator will parse fields. **Gotcha:** it is silently ignored when MCP tools are active.
- `-o/--output-last-message <path>` writes the final message to a file (in addition to stdout).

```bash
codex exec --json "..." | jq -r 'select(.type=="thread.started") | .thread_id'   # session id
codex exec --json "..." | jq 'select(.type=="turn.completed") | .usage'          # tokens
```

## Sessions

- Every run persists in `~/.codex/sessions/` (JSONL); `--ephemeral` runs without persisting.
- Continue the most recent one: `codex exec resume --last "..."`; resume a specific one: `codex exec resume <SESSION_ID> "..."`.
- `--all` on resume sees sessions from any directory (by default only the cwd's).
- Capture the `thread_id` from the `thread.started` event; a follow-up on the same task uses `resume`, a new task creates another session.

## Yolo mode

`--dangerously-bypass-approvals-and-sandbox` (alias `--yolo`) — bypasses approvals **and** the sandbox. It is this skill family's default mode (decision of 2026-07-12): control comes from the orchestrator (isolated worktree, scoped prompt, timeout). **Do not use `--full-auto`** — it is legacy and emits a warning. The fine-grained sandbox (`--sandbox read-only|workspace-write|danger-full-access`) and approval (`-a untrusted|on-request|never`) model exists, but is **not used** here.

## Specific agents

- Profiles: `~/.codex/profile-<NAME>.config.toml`, selected with `-p <name>` — they bundle model/config per task type.
- The repo's `AGENTS.md` and the global `~/.codex/AGENTS.md` are read automatically, including in `exec`.
- Skills (experimental): `~/.codex/skills/**/SKILL.md` also apply in headless mode.
- Subagents are behind the `multi_agent` feature flag — don't count on them by default.

## Model

- `-m/--model <name>` overrides the config: `gpt-5.5`, `gpt-5.4-mini`, `gpt-5.3-codex`, `gpt-5.1-codex-mini`…
- `--oss` uses a local open-source provider; alternative providers (Azure etc.) via `model_provider` + `env_key` in `config.toml`.
- GPT-5.5 may not be available with API key auth in some configurations — test before pinning the model.

## MCP

Servers in `[mcp_servers.NAME]` in `~/.codex/config.toml` (stdio: `command`/`args`; remote: `url` + `bearer_token_env_var`) — `exec` inherits the config. The client prioritizes STDIO; a remote server may require a proxy. `codex mcp-server` goes the other way: it exposes codex as an MCP server.

## Context and directories

- `--cd/-C <path>` sets the workspace root — point it to the task's worktree; `--add-dir <path>` grants write access to extra directories.
- `CODEX_HOME` changes the config/sessions root (default `~/.codex`) — useful for isolating config per orchestrator.
- `--image/-i <path>` (repeatable) attaches images to the prompt.
- Determinism in CI: `--ignore-user-config` (doesn't load the global config) and `--ignore-rules`.

## Auth

Precondition: already logged in (`codex login` already done by the human, or `CODEX_API_KEY` in the environment). **Do not configure login in this skill.** Mechanical check before invoking: `codex login status` (exit 0 = logged in). If the output mentions credential/API key/login/401: **abort the orchestrator's entire task** — no retry, no fallback; an immediate failure with **no** auth signal is an invocation error, not a login one (rule 2 of `delegate-coding`). Gotcha: `OPENAI_API_KEY` in the env makes codex **silently** switch from the ChatGPT plan to API key (separate billing) — don't export that variable without intent.

## Gotchas

- **No per-run cost cap** in the local CLI — only the OpenAI dashboard budget; the ChatGPT plan drains the same quota as the interactive session. The circuit breaker is the OS `timeout` (+ a mini model to reduce tokens).
- `--output-schema` silently ignored with MCP tools active (above).
- Old versions of `codex exec --json` didn't return the session id — parse the `thread.started`.
- Resume "can't find" a session created in another directory — use `--all`.

## Recipes

```bash
# Read-only audit by nature of the prompt, JSONL output
timeout 600 codex exec --dangerously-bypass-approvals-and-sandbox --json \
  "Audit src/auth/ for security issues; do not modify files" | jq 'select(.type=="item.completed")'

# Editing task in the task's worktree, explicit model
timeout 900 codex exec --dangerously-bypass-approvals-and-sandbox --json \
  --cd /path/worktree -m gpt-5.3-codex "Fix bug X in src/login.ts; run the tests; do not touch other files"

# Structured output validated by schema (no MCP active!)
timeout 600 codex exec --dangerously-bypass-approvals-and-sandbox \
  --output-schema schema.json -o result.json "Score open PRs by risk (1-10)"

# Follow-up on the same task
timeout 600 codex exec resume --last --dangerously-bypass-approvals-and-sandbox --json "Now run the full test suite"
```

## See also

- Contract and choice: `delegate-coding` · Same operation in another tool: `run-cursor-agent`, `run-opencode`.
