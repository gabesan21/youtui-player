---
name: run-droid
description: Invokes Factory's droid CLI as a headless executor of coding tasks (droid exec, autonomy levels, sessions, JSON output). Use when delegating coding work to droid via CLI - general contract and tool choice in the delegate-coding skill.
---

# run-droid

Contract, yolo/auth rules and checklist: skill `delegate-coding` — read it before the first delegation. Before the first invocation on the machine, confirm the flags with `droid exec --help` — versions diverge (source: Factory's official docs read on 2026-07-16).

## Headless invocation

```bash
timeout 600 droid exec --skip-permissions-unsafe -o json "scoped task"
```

- `droid exec` runs without the TUI until completion and exits with a status code — never call bare `droid` in automation (it opens the TUI).
- Prompt: positional argument, file (`-f/--file prompt.md`) or pipe (`echo "task" | droid exec`).
- **Autonomy fail-fast:** if the autonomy level doesn't cover a requested action, droid stops immediately with a clear error, exit ≠ 0 and **no partial changes**.
- Exit code: `0` success; ≠ 0 failure (permission violation, tool error, unmet objective) — treat as a pipeline failure.

## Output and parsing

- `-o/--output-format text|json|stream-jsonrpc`. The `json` is a **single object** at the end (not NDJSON): `{type:"result", subtype, is_error, duration_ms, num_turns, result, session_id}`.
- `stream-jsonrpc` is a bidirectional line-based JSON-RPC protocol (requests on stdin) for custom integrations — for normal orchestration, use `json`.

```bash
droid exec --skip-permissions-unsafe -o json "..." | jq -r '.result'       # final answer
droid exec --skip-permissions-unsafe -o json "..." | jq -r '.session_id'   # session id
```

## Sessions

- Continue: `droid exec -s/--session-id <id> "..."` (requires a new prompt); branch with a new id: `--fork <id>`.
- Interactive: `droid --resume [id]` (default: last modified); search across sessions: `droid search "..."`.
- `--tag <spec>` (repeatable) and `--log-group-id <id>` label and group runs — useful for CI observability.
- Capture the `session_id` from the result JSON; a follow-up on the same task uses `-s`, a new task creates another session.

## Yolo mode

`--skip-permissions-unsafe` — complete confirmation bypass, the default mode of this skill family (decision of 2026-07-12): control comes from the orchestrator (isolated worktree, scoped prompt, timeout). **It does not combine with `--auto`** (mutually exclusive). The native autonomy ladder (`no flag` = read-only; `--auto low` creates/edits files; `medium` installs deps, network, commit; `high` push and arbitrary execution) is mapped, but **not used** here — except the read-only default, useful for recon.

## Specific agents

- `--use-spec` starts in specification mode (plans before executing); `--spec-model`/`--spec-reasoning-effort` configure the spec phase.
- Mission mode (`--mission` + `--worker-model`/`--validator-model` and efforts) orchestrates multi-agent **inside** droid — no normal use here: the orchestrator is the PoP.
- `--append-system-prompt <text>` / `--append-system-prompt-file <path>` append guidance to the system prompt.
- The repo's `AGENTS.md` is read natively; custom droids, slash commands and skills via config (`~/.factory/`).

## Model

- `-m/--model <id>`: `claude-sonnet-4-6`, `claude-opus-4-8`, `gpt-5.5`, `gpt-5.3-codex`, `gemini-3.1-pro-preview`, open models (`glm-5.2`, `kimi-k2.7-code`…) — each with its own billing multiplier (`-fast` variants cost more).
- `-r/--reasoning-effort <level>` overrides the model's default (the default varies per model).
- BYOK: `customModels` in `~/.factory/settings.json`, referenced as `custom:<displayName>-0`.
- **Which model:** the explicit human invocation or the coding-agent harness chooses it; task size does not select a model and PoP has no central model catalog.

## MCP

- `droid mcp add <name> <url> --type http|sse` (remote) or `droid mcp add <name> "<command>"` (local stdio); `droid mcp remove <name>` removes — `exec` inherits the config.

## Context and directories

- `--cwd <path>` sets the execution directory — point it to the task's worktree.
- Native git worktree in a flag: `-w/--worktree [name]` (separate branch) + `--worktree-dir <path>`.
- `--enabled-tools`/`--disabled-tools` restrict tools per invocation; `--list-tools` lists the ones available for the model.

## Auth

Precondition: already logged in (droid login already done by the human, or `FACTORY_API_KEY` in the environment — key generated at app.factory.ai/settings/api-keys). **Do not configure login in this skill.** If the output mentions credential/API key/login/401: **abort the orchestrator's entire task** — no retry, no fallback; an immediate failure with **no** auth signal is an invocation error, not a login one (rule 2 of `delegate-coding`).

## Gotchas

- `--skip-permissions-unsafe` and `--auto` are mutually exclusive — passing both is an error.
- Exit ≠ 0 with a permission error is not a bug: it's the autonomy fail-fast (level insufficient for what the prompt asked) — it doesn't happen in the family's yolo mode.
- `stream-jsonrpc` expects requests on stdin — it is not a passive event stream; for simple parsing stay on `-o json`.
- Billing multipliers vary a lot per model — open models and `claude-haiku-4-5-20251001` cut cost on light tasks.

## Recipes

```bash
# Edit task in the task's worktree, explicit model, JSON output
timeout 900 droid exec --skip-permissions-unsafe -o json --cwd /path/worktree \
  -m claude-sonnet-4-6 "Fix bug X in src/login.ts; run the tests; do not touch other files" | jq -r '.result'

# Recon that is read-only by nature (default with no autonomy flag)
timeout 600 droid exec -o json "Audit src/auth/ for security issues; do not modify files"

# Prompt from a file + labels for CI
timeout 900 droid exec --skip-permissions-unsafe -f prompt.md -o json --tag ci --log-group-id build-123

# Follow-up in the same session
timeout 600 droid exec --skip-permissions-unsafe -s <session_id> -o json "Now run the full test suite"
```

## See also

- Contract and choice: `delegate-coding` · Same operation in another tool: `run-cursor-agent`, `run-opencode`, `run-codex`.
- Source: Factory's official docs (https://docs.factory.ai/cli/droid-exec/overview) — skill written straight from the docs on 2026-07-16, with no synthesis in `researches/`.
