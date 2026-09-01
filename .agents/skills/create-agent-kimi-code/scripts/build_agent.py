#!/usr/bin/env python3
"""Build and structurally validate Kimi Code projections of canonical PoP roles."""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import re
import sys
import tomllib

GUARANTEE_GAPS = {"effective-model-effort", "max-agent-nesting", "aggregate-agent-validation"}
KNOWN_FIELDS = {"name", "description", "whenToUse", "override", "model_preference", "tools", "disallowedTools", "subagents"}
REQUIRED_SECTIONS = (
    "Identity", "Trigger", "Context acquisition by path", "Permissions",
    "Input, output, and termination", "Ownership", "Dependencies", "Gates and re-entry", "Denies",
)
ROLE_POLICY = {
    "pop-planner": {
        "tools": ["Read", "Grep", "Glob", "Write", "Edit", "Agent"],
        "denied": ["Bash", "WebSearch", "FetchURL", "AgentSwarm"], "subagents": ["pop-recon"],
    },
    "pop-recon": {
        "tools": ["Read", "Grep", "Glob", "Write", "Edit"],
        "denied": ["Bash", "WebSearch", "FetchURL", "Agent", "AgentSwarm"], "subagents": [],
    },
    "pop-execution-orchestrator": {
        "tools": ["Read", "Grep", "Glob", "Agent", "AgentSwarm"],
        "denied": ["Bash", "Write", "Edit", "WebSearch", "FetchURL"], "subagents": ["pop-executor"],
    },
    "pop-executor": {
        "tools": ["Read", "Grep", "Glob", "Bash", "Write", "Edit"],
        "denied": ["WebSearch", "FetchURL", "Agent", "AgentSwarm"], "subagents": [],
    },
    "pop-judge-dredd": {
        "tools": ["Read", "Grep", "Glob", "Bash", "Write", "Edit"],
        "denied": ["WebSearch", "FetchURL", "Agent", "AgentSwarm"], "subagents": [],
    },
    "pop-phase-verifier": {
        "tools": ["Read", "Grep", "Glob", "Bash", "Write", "Edit"],
        "denied": ["WebSearch", "FetchURL", "Agent", "AgentSwarm"], "subagents": [],
    },
}
SWARM_INSTRUCTIONS = {
    "pop-execution-orchestrator": (
        "AgentSwarm may launch only multiple independent pop-executor instances. Use Agent for a single "
        "executor, a dependency, or required serialization. Agent and AgentSwarm share the subagents "
        "allowlist; this distinction by call type is a role obligation, not native runtime enforcement."
    ),
}
SOURCE_MARKER = "<!-- canonical-source-sha256: {digest} -->"


class BuildError(ValueError):
    pass


def fail(message: str) -> None:
    raise BuildError(message)


def read_source(path: Path) -> tuple[str, str]:
    role = path.stem
    if role not in ROLE_POLICY:
        fail(f"non-canonical role: {role}")
    body = path.read_text(encoding="utf-8").rstrip() + "\n"
    missing = [section for section in REQUIRED_SECTIONS if f"## {section}" not in body]
    if missing:
        fail("incomplete canonical body: " + ", ".join(missing))
    return role, body


def yaml_list(name: str, values: list[str]) -> list[str]:
    return [f"{name}: []"] if not values else [f"{name}:", *(f"  - {value}" for value in values)]


def render_agent(role: str, body: str, routing: str) -> str:
    policy = ROLE_POLICY[role]
    swarm_instruction = SWARM_INSTRUCTIONS.get(role)
    runtime_instructions = (
        ["## Kimi coordination instruction", "", swarm_instruction, ""]
        if swarm_instruction else []
    )
    identity = re.search(r"## Identity\n\n([^\n]+)", body)
    trigger = re.search(r"## Trigger\n\n([^\n]+)", body)
    if not identity or not trigger:
        fail("identity or trigger not found in the canonical body")
    lines = [
        "---", f"name: {role}", f"description: {identity.group(1)}", f"whenToUse: {trigger.group(1)}",
        "override: false", f"model_preference: {routing}", *yaml_list("tools", policy["tools"]),
        *yaml_list("disallowedTools", policy["denied"]), *yaml_list("subagents", policy["subagents"]),
        "---", "", SOURCE_MARKER.format(digest=hashlib.sha256(body.encode()).hexdigest()), "",
        "This projection preserves the complete canonical contract below. Path restrictions remain role obligations, not a runtime sandbox.",
        "The final message must be the complete, self-contained result for the caller.", "",
        *runtime_instructions, body.rstrip(), "",
    ]
    return "\n".join(lines)


def reject_unsupported_effort(config: dict[str, object], alias: str, effort: str) -> None:
    models = config.get("models")
    if not isinstance(models, dict):
        fail("config without a [models] table")
    model_entry = models.get(alias)
    if not isinstance(model_entry, dict):
        fail(f"secondary model alias unresolved in [models]: {alias}")
    effective_model = model_entry.get("model")
    if not isinstance(effective_model, str) or not effective_model:
        fail(f"[models] entry without an effective model: {alias}")
    is_k27 = re.search(r"(?:kimi-for-coding|k2[.-]?7)", f"{alias} {effective_model}", re.I)
    if effort == "medium" and is_k27:
        fail("K2.7 medium is not a demonstrated effective effort")


def render_config_candidate(source: Path, output: Path, model: str, effort: str | None = None) -> None:
    if source.resolve() == output.resolve():
        fail("source and candidate configs must be different paths")
    kimi_home = Path(os.environ.get("KIMI_CODE_HOME", Path.home() / ".kimi-code"))
    if output.resolve() == (kimi_home / "config.toml").resolve():
        fail("editing the active config is forbidden; use a separate candidate")
    raw = source.read_text(encoding="utf-8")
    try:
        parsed = tomllib.loads(raw)
    except tomllib.TOMLDecodeError as error:
        fail(f"invalid source config: {error}")
    if "secondary_model" in parsed:
        fail("source config already has [secondary_model]; refusing implicit overwrite")
    if not re.fullmatch(r"[A-Za-z0-9._:/+-]+", model):
        fail("invalid secondary model alias")
    if effort is not None:
        if not re.fullmatch(r"[a-z0-9_-]+", effort):
            fail("invalid secondary effort")
        reject_unsupported_effort(parsed, model, effort)
    suffix = ("\n" if raw.endswith("\n") else "\n\n") + f'[secondary_model]\nmodel = "{model}"\n'
    if effort is not None:
        suffix += f'default_effort = "{effort}"\n'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(raw + suffix, encoding="utf-8")


def parse_generated_agent(raw: str) -> tuple[dict[str, object], str]:
    if not raw.startswith("---\n") or "\n---\n" not in raw[4:]:
        fail("missing or invalid frontmatter")
    header, body = raw[4:].split("\n---\n", 1)
    fields: dict[str, object] = {}
    current: str | None = None
    for line in header.splitlines():
        if line.startswith("  - "):
            if current is None or not isinstance(fields[current], list):
                fail("YAML item without a list")
            fields[current].append(line[4:])
            continue
        if ":" not in line:
            fail(f"invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        current = key
        fields[key] = [] if value.strip() in {"", "[]"} else value.strip()
    unknown = set(fields) - KNOWN_FIELDS
    if unknown:
        fail("unknown Kimi fields: " + ", ".join(sorted(unknown)))
    return fields, body


def validate_agent(source: Path, agent: Path, routing: str, config: Path | None) -> None:
    role, canonical = read_source(source)
    raw_agent = agent.read_text(encoding="utf-8")
    fields, generated_body = parse_generated_agent(raw_agent)
    if set(fields) != KNOWN_FIELDS:
        fail("frontmatter does not contain exactly the expected Kimi fields")
    if raw_agent != render_agent(role, canonical, routing):
        fail("agent differs from the deterministic projection of the source")
    if fields.get("name") != role or fields.get("model_preference") != routing:
        fail("name or routing differs from the request")
    policy = ROLE_POLICY[role]
    for field, expected in (("tools", policy["tools"]), ("disallowedTools", policy["denied"]), ("subagents", policy["subagents"])):
        if fields.get(field) != expected:
            fail(f"{field} differs from the role's fail-closed policy")
    digest = hashlib.sha256(canonical.encode()).hexdigest()
    if SOURCE_MARKER.format(digest=digest) not in generated_body or not generated_body.rstrip().endswith(canonical.rstrip()):
        fail("canonical body was not fully preserved")
    if routing == "secondary":
        if config is None:
            fail("secondary routing requires a candidate config")
        try:
            parsed = tomllib.loads(config.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as error:
            fail(f"invalid candidate config: {error}")
        secondary = parsed.get("secondary_model")
        if not isinstance(secondary, dict) or not isinstance(secondary.get("model"), str):
            fail("candidate config without [secondary_model].model")
        effort = secondary.get("default_effort")
        if effort is not None:
            if not isinstance(effort, str):
                fail("[secondary_model].default_effort must be a string when present")
            reject_unsupported_effort(parsed, secondary["model"], effort)


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--require-guarantee", action="append", choices=sorted(GUARANTEE_GAPS), default=[])


def make_parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    commands = root.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build")
    add_common(build)
    build.add_argument("--source", type=Path, required=True)
    build.add_argument("--agent-out", type=Path, required=True)
    build.add_argument("--routing", choices=("primary", "secondary"), required=True)
    build.add_argument("--config-source", type=Path)
    build.add_argument("--config-out", type=Path)
    build.add_argument("--secondary-model")
    build.add_argument("--secondary-effort")
    validate = commands.add_parser("validate")
    add_common(validate)
    validate.add_argument("--source", type=Path, required=True)
    validate.add_argument("--agent", type=Path, required=True)
    validate.add_argument("--routing", choices=("primary", "secondary"), required=True)
    validate.add_argument("--config", type=Path)
    return root


def main() -> int:
    args = make_parser().parse_args()
    try:
        if args.require_guarantee:
            fail("undemonstrated guarantee: " + ", ".join(args.require_guarantee))
        if args.command == "build":
            role, body = read_source(args.source)
            if args.routing == "secondary":
                required = (args.config_source, args.config_out, args.secondary_model)
                if not all(required):
                    fail("secondary requires source/candidate config and model")
                render_config_candidate(args.config_source, args.config_out, args.secondary_model, args.secondary_effort)
            args.agent_out.parent.mkdir(parents=True, exist_ok=True)
            args.agent_out.write_text(render_agent(role, body, args.routing), encoding="utf-8")
            print("projection generated and validatable without running a coding agent")
        else:
            validate_agent(args.source, args.agent, args.routing, args.config)
            print("structure, policy, candidate config and canonical body are locally valid")
    except (BuildError, OSError) as error:
        print(f"BLOCKED: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
