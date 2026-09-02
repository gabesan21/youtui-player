# internal/ui — TUI layer and concurrency rules

> Trigger: edit this contract before changing widgets, event handlers, playback goroutines, theme/language wiring or state restoration.

- **Never** mutate tview primitives from background goroutines; always use `app.QueueUpdateDraw()`.
  <!-- pop-hash: app.go sha256=52a83a29894889f7d5171fe04a9181d0e822acfa7b3a8537defb9079d7e7b8c8 -->
- `SimpleApp.mu` guards shared state; lock before accessing `tracks`, `playlistTracks`, `currentTrack` or playback flags from any goroutine.
- `player_live_test.go` contains a live network test skipped under `-short`; do **not** make it required in `make test` or CI.
  <!-- pop-hash: player_live_test.go sha256=5bf9a5df9a09c0767db534b47e4f5e1d4eaa046e9fb5d69965cbcadb18418c4d -->
- Language changes flow through `applyLanguage()`; keep `internal/search.SetTexts()` in sync when adding new search error strings.
  <!-- pop-hash: setup.go sha256=b1b85702aad6c1f1d8f2d82c2ee961bc68581a022ef4f0197781dd87ed2f0dea -->
- Theme changes rebuild `HelpView` because it bakes colors at construction time.
- Do **not** add direct database, network or filesystem I/O in event handlers; delegate to `internal/search` or `internal/config`.
- Thumbnail fetches run in background goroutines and must queue UI updates through `app.QueueUpdateDraw()`.
- `CustomList` indexes are local to the current page; account for `pagination.GetPageItems()` offsets when mapping to `tracks`.
- Do **not** import `internal/ui/components/` into the root UI files without updating this contract; components are not yet covered by a child contract.
- State restoration happens asynchronously after `NewSimpleApp()` returns; do **not** assume the playlist is populated during construction.

## Related contracts

- `../search/AGENTS.md` — follow when changing `yt-dlp` search calls or the error strings passed to `search.SetTexts()`.
- `../config/AGENTS.md` — follow when reading/writing config or session state from the UI.
