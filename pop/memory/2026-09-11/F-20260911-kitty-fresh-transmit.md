---
task: F-20260911-kitty-fresh-transmit
project: youtui-player
started: 2026-09-11
finished: 2026-09-11
commit: c27c207
pr:
authorization: F-20260911-kitty-fresh-transmit: direct-fix triage (rule 13)
---

# F-20260911-kitty-fresh-transmit — single-use Kitty image ids

- **Delivery:** every Kitty placement emits a fresh `a=t` transmit (new image id) and placement id; deletes use `d=I` (placement + data); the `transmitted` dedup map is gone.
- **Verification:** `make build`/`fmt`/`vet` green; no tests per workflow; Kitty validation stays with the human (`YOUTUI_KITTY_DEBUG`).
- **Contract impact:** specs: [[pop/specs/ui-thumbnails|ui-thumbnails]] invariant replaced · DOX: `internal/ui/AGENTS.md` kitty rule updated.

## Entries

- [[F-20260911-kitty-fresh-transmit.01-single-use-image-ids]] — same-image-id overlap is undefined; fresh transmit per place.
- [[F-20260911-kitty-fresh-transmit.02-delete-frees-image-data]] — `d=p`→`d=I`; deleting may free image data in real terminals.

## Links

- **Origin:** user's real-Kitty debug log after M-2.1 (perfect emissions, screen still stale) — *follow for why this fix exists*.
- **Commit:** c27c207 — *follow to inspect the final diff*.
