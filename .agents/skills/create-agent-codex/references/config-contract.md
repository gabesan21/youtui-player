# Codex configuration contract

## Closed local profile

- Standalone keys: `name`, `description`, `developer_instructions`, `model`, `model_reasoning_effort`, `sandbox_mode`.
- Models: `gpt-5.6-sol`, `gpt-5.6-terra`.
- Effort: `minimal`, `low`, `medium`, `high`, `xhigh`.
- Sandbox: `read-only`, `workspace-write`, `danger-full-access`.

The identifiers are stored as local configuration. The builder does not test accounts, providers, availability, or model responses.

## Validation boundary

Validation covers TOML parsing, a closed schema, non-empty strings, local enums, filename/path, and SHA-256. `validate-static` and `promote` require the canonical Markdown and recreate the projection with the candidate tuple; any body or byte difference fails before writing. Repeated rendering/promotion proves determinism and idempotence. No command starts a session, prompt, model, authentication, network, or provider call.

## Safe writes

`render` and `promote` write a temporary file next to the destination, synchronize it, and rename atomically. `promote` accepts only `.codex/agents/<name>.toml`. An existing destination requires `--replace` and must still match the same canonical source and `name`. Every validation finishes before replacement.
