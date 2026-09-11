---
task: F-20260911-kitty-crop-clamp
project: youtui-player
started: 2026-09-11
finished: 2026-09-11
commit: 05c3ab0
pr:
authorization: F-20260911-kitty-crop-clamp: direct-fix triage (rule 13)
---

# F-20260911-kitty-crop-clamp — Kitty thumbnails: aspect crop and panel clamping

- **Delivery:** Kitty thumbnails keep aspect (centered source-crop placement, cell pixel size via TIOCGWINSZ) and are clipped to their owning panel (rect intersection; fully clipped rows place nothing).
- **Verification:** `make build`/`make fmt`/`make vet` green; no tests per workflow; empirical Kitty validation remains the human's.
- **Contract impact:** specs: [[pop/specs/ui-thumbnails|ui-thumbnails]] Output + invariants updated · DOX: `internal/ui/AGENTS.md` kitty rule updated, hashes refreshed.

## Entries

- [[F-20260911-kitty-crop-clamp.01-aspect-source-crop]] — centered source crop preserves aspect without re-encoding.
- [[F-20260911-kitty-crop-clamp.02-panel-clamping]] — placements clamped to the owning panel; leaks fixed.

## Links

- **Origin:** human test report after F-20260911-kitty-png-fix — *follow for the symptoms (stretch, leaks)*.
- **Commit:** 05c3ab0 — *follow to inspect the final diff*.
