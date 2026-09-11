---
task: F-20260911-kitty-fresh-transmit
project: youtui-player
started: 2026-09-11
finished: 2026-09-11
commit: c27c207
pr:
authorization: F-20260911-kitty-fresh-transmit: direct-fix triage (rule 13)
---

# F-20260911-kitty-fresh-transmit — Kitty image ids are single-use (fresh transmit per place, d=I delete)

- **Delivery:** every Kitty placement emits a fresh `a=t` transmit (new image id) plus a fresh placement id; deletes use `d=I` (placement AND image data); the `transmitted` dedup map is gone.
- **Verification:** `make build`/`make fmt`/`make vet` green; no tests per workflow; empirical Kitty validation stays with the human (debug log `YOUTUI_KITTY_DEBUG`).
- **Contract impact:** specs: [[pop/specs/ui-thumbnails|ui-thumbnails]] invariant replaced (single-use image ids, d=I) · DOX: `internal/ui/AGENTS.md` kitty rule updated.

## Entries

- [[F-20260911-kitty-fresh-transmit.01-single-use-image-ids]] — same-image-id overlap is undefined; fresh transmit per place.
- [[F-20260911-kitty-fresh-transmit.02-delete-frees-image-data]] — `d=p`→`d=I`; deleting may free image data in real terminals.

## Links

- **Origin:** user's real-Kitty debug log after M-2.1 (perfect emissions, screen still stale) — *follow for why this fix exists*.
- **Commit:** c27c207 — *follow to inspect the final diff*.
