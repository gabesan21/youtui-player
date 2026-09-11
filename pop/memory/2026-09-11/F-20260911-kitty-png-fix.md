---
task: F-20260911-kitty-png-fix
project: youtui-player
started: 2026-09-11
finished: 2026-09-11
commit: 2f84a86
pr:
authorization: F-20260911-kitty-png-fix: direct-fix triage (rule 13)
---

# F-20260911-kitty-png-fix — Kitty thumbnails invisible: PNG transmission fix

- **Delivery:** Kitty thumbnails render again: the sink now transmits a derived PNG (kitty accepts RGB/RGBA/PNG only, not the JPEG cache), transmit is `a=t` (no display at cursor), and Invalidate re-transmits after delete-all.
- **Verification:** `make build`/`make fmt`/`make vet` green; no tests per workflow; empirical Kitty validation assigned to the human (criteria 8–9 of M-1.1).
- **Contract impact:** specs: [[pop/specs/ui-thumbnails|ui-thumbnails]] Interfaces updated (derived PNG) · DOX: `internal/ui/AGENTS.md` kitty rule updated.

## Entries

- [[F-20260911-kitty-png-fix.01-png-derivation]] — JPEG cache rejected by kitty; PNG derivation added.
- [[F-20260911-kitty-png-fix.02-transmit-only-and-retransmit]] — `a=T`→`a=t`; Invalidate drops the transmitted registry.

## Links

- **Origin:** user bug report after M-1.1-kitty-thumbnails — *follow for why this fix exists*.
- **Commit:** 2f84a86 — *follow to inspect the final diff*.
