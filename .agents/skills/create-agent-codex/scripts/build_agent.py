#!/usr/bin/env python3
"""Render and validate standalone Codex custom-agent TOML files."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import tomllib
from pathlib import Path
from typing import Any

REQUIRED_KEYS = {
    "name",
    "description",
    "developer_instructions",
    "model",
    "model_reasoning_effort",
    "sandbox_mode",
}
MODELS = {"gpt-5.6-sol", "gpt-5.6-terra"}
EFFORTS = {"minimal", "low", "medium", "high", "xhigh"}
SANDBOX_MODES = {"read-only", "workspace-write", "danger-full-access"}
ROLE_SECTIONS = (
    "Identity",
    "Trigger",
    "Context acquisition by path",
    "Permissions",
    "Input, output, and termination",
    "Ownership",
    "Dependencies",
    "Gates and re-entry",
    "Denies",
)
ROLE_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class Invalid(ValueError):
    """Input or static schema is invalid."""


class Collision(ValueError):
    """An existing output cannot be replaced safely."""


def nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Invalid(f"{field} must be a non-empty string")
    return value


def parse_role(source: Path) -> tuple[str, str, str]:
    try:
        body = source.read_text(encoding="utf-8")
    except OSError as exc:
        raise Invalid(f"could not read the role: {source}: {exc}") from exc

    heading = re.match(r"\A# ([^\n]+)\n", body)
    if not heading:
        raise Invalid("role must start with an H1 heading")
    name = heading.group(1).strip()
    if not ROLE_NAME.fullmatch(name):
        raise Invalid(f"invalid role name: {name!r}")

    sections: dict[str, str] = {}
    matches = list(re.finditer(r"(?m)^## ([^\n]+)\n", body))
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        sections[match.group(1).strip()] = body[match.end() : end].strip()
    missing = [section for section in ROLE_SECTIONS if not sections.get(section)]
    if missing:
        raise Invalid("missing/empty canonical sections: " + ", ".join(missing))

    description = " ".join(sections["Trigger"].split())
    instructions = (
        "Native Codex projection of a canonical PoP contract. "
        "Preserve every power, limit, direct-acquisition rule, ownership constraint, and deny below; "
        "the sandbox does not replace these obligations.\n\n"
        + body.rstrip()
        + "\n"
    )
    return name, description, instructions


def toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_agent(source: Path, model: str, effort: str, sandbox_mode: str) -> bytes:
    if model not in MODELS:
        raise Invalid(f"model outside the local allowlist: {model}")
    if effort not in EFFORTS:
        raise Invalid(f"model_reasoning_effort outside the local allowlist: {effort}")
    if sandbox_mode not in SANDBOX_MODES:
        raise Invalid(f"sandbox_mode outside the local allowlist: {sandbox_mode}")
    name, description, instructions = parse_role(source)
    values = {
        "name": name,
        "description": description,
        "developer_instructions": instructions,
        "model": model,
        "model_reasoning_effort": effort,
        "sandbox_mode": sandbox_mode,
    }
    lines = [f"{key} = {toml_string(values[key])}" for key in values]
    candidate = ("\n".join(lines) + "\n").encode("utf-8")
    validate_static_bytes(candidate)
    return candidate


def validate_static_bytes(content: bytes) -> dict[str, str]:
    try:
        document = tomllib.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise Invalid(f"invalid TOML: {exc}") from exc
    keys = set(document)
    if keys != REQUIRED_KEYS:
        missing = sorted(REQUIRED_KEYS - keys)
        extra = sorted(keys - REQUIRED_KEYS)
        raise Invalid(f"divergent standalone schema; missing={missing}; extra={extra}")
    for key in REQUIRED_KEYS:
        nonempty_string(document[key], key)
    if not ROLE_NAME.fullmatch(document["name"]):
        raise Invalid("name is not in kebab-case")
    if document["model"] not in MODELS:
        raise Invalid(f"model outside the local allowlist: {document['model']}")
    if document["model_reasoning_effort"] not in EFFORTS:
        raise Invalid("model_reasoning_effort outside the local allowlist")
    if document["sandbox_mode"] not in SANDBOX_MODES:
        raise Invalid("sandbox_mode outside the local allowlist")
    return document


def validate_against_source(content: bytes, source: Path) -> dict[str, str]:
    """Validate structure and exact deterministic projection from a canonical role."""
    agent = validate_static_bytes(content)
    expected = render_agent(
        source,
        agent["model"],
        agent["model_reasoning_effort"],
        agent["sandbox_mode"],
    )
    if expected != content:
        raise Invalid("agent differs from the deterministic projection of the canonical source")
    return agent


def read_bytes(path: Path, label: str) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        raise Invalid(f"could not read {label}: {path}: {exc}") from exc


def atomic_write(
    path: Path,
    content: bytes,
    replace: bool,
    expected_name: str,
    source: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if not replace:
            raise Collision(f"destination already exists: {path}; use --replace deliberately")
        try:
            current = validate_against_source(path.read_bytes(), source)
        except (OSError, Invalid) as exc:
            raise Collision(f"existing destination cannot be safely replaced: {exc}") from exc
        if current["name"] != expected_name:
            raise Collision("existing destination belongs to another agent")

    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as handle:
            temporary = handle.name
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except OSError as exc:
        raise Invalid(f"atomic write failure at {path}: {exc}") from exc
    finally:
        if temporary:
            try:
                Path(temporary).unlink(missing_ok=True)
            except OSError:
                pass


def require_agent_destination(path: Path, expected_name: str) -> None:
    if path.parent.name != "agents" or path.parent.parent.name != ".codex":
        raise Invalid("final destination must be under .codex/agents/")
    if path.name != f"{expected_name}.toml":
        raise Invalid("destination name must match the agent's name")


def reject_render_agent_destination(path: Path) -> None:
    normalized_parts = path.resolve(strict=False).parts
    if any(
        part == ".codex"
        and index + 1 < len(normalized_parts)
        and normalized_parts[index + 1] == "agents"
        for index, part in enumerate(normalized_parts)
    ):
        raise Invalid("render cannot write under .codex/agents/; use promote")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    render = commands.add_parser("render", help="render a statically valid candidate")
    render.add_argument("source", type=Path)
    render.add_argument("candidate", type=Path)
    render.add_argument("--model", required=True)
    render.add_argument("--effort", required=True)
    render.add_argument("--sandbox-mode", required=True)
    render.add_argument("--replace", action="store_true")

    static = commands.add_parser("validate-static", help="validate structure and allowlists only")
    static.add_argument("agent", type=Path)
    static.add_argument("--source", required=True, type=Path)

    promote = commands.add_parser("promote", help="promote a locally validated candidate")
    promote.add_argument("candidate", type=Path)
    promote.add_argument("output", type=Path)
    promote.add_argument("--source", required=True, type=Path)
    promote.add_argument("--replace", action="store_true")
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "render":
            reject_render_agent_destination(args.candidate)
            content = render_agent(args.source, args.model, args.effort, args.sandbox_mode)
            agent = validate_static_bytes(content)
            atomic_write(args.candidate, content, args.replace, agent["name"], args.source)
            digest = hashlib.sha256(content).hexdigest()
            print(f"LOCAL_OK name={agent['name']} sha256={digest}")
        else:
            content = read_bytes(args.agent if args.command == "validate-static" else args.candidate, "agent")
            agent = validate_against_source(content, args.source)
            if args.command == "validate-static":
                digest = hashlib.sha256(content).hexdigest()
                print(f"LOCAL_OK name={agent['name']} sha256={digest}")
            else:
                require_agent_destination(args.output, agent["name"])
                atomic_write(args.output, content, args.replace, agent["name"], args.source)
                digest = hashlib.sha256(content).hexdigest()
                print(f"OK promoted name={agent['name']} sha256={digest} output={args.output}")
        return 0
    except Collision as exc:
        print(f"COLLISION: {exc}", file=sys.stderr)
        return 4
    except Invalid as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
