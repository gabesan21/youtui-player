---
name: sync-specs
description: Mandatory spec synchronization as tasks advance; use in 002, 004, 005_closing, and spec-drift audits.
---

# sync-specs

**A spec describes the agreed current state. A lying spec is a bug.**

| Stage | Obligation |
|---|---|
| 002 | Identify affected durable contracts. Link existing specs; create canonical `draft/planned` only for a new promise. |
| 003 | Approval activates proposed drafts; implementation remains evidence-based. |
| 004 | Record implementation/spec divergence in Open and the card; material contract change returns to 002. |
| 005_closing | At close-out, in the same wrap-up that writes the memory: reflect delivered reality, resolve relevant questions, and set implementation to partial/implemented/not_applicable. Checking spec impact there is **not optional**. |

Canonical format is [[_templates/SPEC|SPEC]]. `id`, `project`, `domain`, `kind`, `status`, `implementation`, `origin`, dates, `supersedes`, and `superseded_by` are required. A collection opts in atomically with `specs/INDEX.md`; every draft/active spec is reachable directly or through one indexed domain overview. The tree stops at `specs/<domain>/` and supersession links are reciprocal.

Audit `005_closing` cards and linked specs for implementation drift, broken reciprocal supersession, and unreachable current specs. A spec stores durable behavior, invariants, interfaces, errors, and criteria—never reasoning, edit sequence, changelog, or completed-task history.
