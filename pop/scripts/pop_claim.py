#!/usr/bin/env python3
"""pop_claim — task claim (lease): prevents two agents on the same task.

The orchestrator records `claimed_by:`/`claimed_at:` on the card when
taking the task and releases when stopping at a gate. A claim by another
agent still within the lease (default 2h) → refusal with exit 1. An
expired claim may be taken over.

Usage:
    python3 scripts/pop_claim.py <task-id> [--by NAME]          # claim
    python3 scripts/pop_claim.py <task-id> --release [--by NAME]
    python3 scripts/pop_claim.py <task-id> --status
    Options: --lease-hours N (default 2) · --force · --vault DIR
"""

import argparse
import sys

import poplib

DEFAULT_LEASE_HOURS = poplib.DEFAULT_LEASE_HOURS


def set_fields(card, updates):
    """Writes fields to the card's frontmatter (creates the key if missing)."""
    lines = card.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        sys.exit(f"Card without frontmatter: {card}")
    end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    for key, value in updates.items():
        for i in range(1, end):
            if lines[i].startswith(f"{key}:"):
                lines[i] = f"{key}: {value}".rstrip()
                break
        else:
            lines.insert(end, f"{key}: {value}".rstrip())
            end += 1
    card.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Task claim (lease) to avoid duplicated work.")
    parser.add_argument("task_id")
    parser.add_argument("--by", default=poplib.default_agent(),
                        help="agent identifier (default: user@host)")
    parser.add_argument("--release", action="store_true",
                        help="releases the claim instead of taking it")
    parser.add_argument("--status", action="store_true",
                        help="only shows the claim's state")
    parser.add_argument("--lease-hours", type=float, default=DEFAULT_LEASE_HOURS,
                        help=f"claim validity in hours (default {DEFAULT_LEASE_HOURS})")
    parser.add_argument("--force", action="store_true",
                        help="ignores owner/lease (forced release or takeover)")
    parser.add_argument("--scope", "--vault", dest="vault", metavar="DIR")
    args = parser.parse_args()

    root = poplib.vault_root(args.vault)
    found = poplib.find_task(root, args.task_id)
    if not found:
        print(f"Task not found: {args.task_id}")
        return 1
    _project, stage, task_dir = found
    card = task_dir / f"{args.task_id}.md"
    if not card.is_file():
        sys.exit(f"Card not found: {card}")
    meta = poplib.read_card(card)
    by, at = poplib.parse_claim(meta)
    holds = by is not None and not poplib.claim_expired(at, args.lease_hours)

    if args.status:
        if by is None:
            print(f"{args.task_id} [{stage}]: free")
            return 0
        state = "active" if holds else "EXPIRED"
        print(f"{args.task_id} [{stage}]: claim {state} by {by} since "
              f"{at.isoformat(timespec='minutes') if at else '?'}")
        return 1 if holds and by != args.by else 0

    if args.release:
        if by is None:
            print(f"{args.task_id}: was already free.")
            return 0
        if by != args.by and not args.force:
            print(f"{args.task_id}: the claim belongs to {by}, not {args.by} — "
                  f"use --force to release it anyway.")
            return 1
        set_fields(card, {"claimed_by": "", "claimed_at": ""})
        print(f"{args.task_id}: claim released.")
        return 0

    # claim
    if holds and by != args.by and not args.force:
        print(f"{args.task_id} [{stage}]: BUSY — active claim by {by} since "
              f"{at.isoformat(timespec='minutes')} (lease {args.lease_hours}h). "
              f"Do not work on this task.")
        return 1
    if by and by != args.by:
        why = "expired" if not holds else "forced (--force)"
        print(f"{args.task_id}: taking over {why} claim from {by}.")
    set_fields(card, {"claimed_by": args.by,
                      "claimed_at": poplib.now().isoformat(timespec="minutes")})
    print(f"{args.task_id} [{stage}]: claim registered for {args.by} "
          f"(lease {args.lease_hours}h — renew by re-claiming).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
