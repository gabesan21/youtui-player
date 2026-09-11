# internal/ui — TUI layer and concurrency rules

> Trigger: edit this contract before changing widgets, event handlers, playback goroutines, theme/language wiring or state restoration.

- **Never** mutate tview primitives from background goroutines; always use `app.QueueUpdateDraw()`.
  <!-- pop-hash: app.go sha256=60c7d4080f0a28c85dc7e8c1f1bbebc82dfffec23db05a244496695014d45244 -->
- `SimpleApp.mu` guards shared state; lock before accessing `tracks`, `playlistTracks`, `currentTrack` or playback flags from any goroutine.
- `player_live_test.go` contains a live network test skipped under `-short`; do **not** make it required in `make test` or CI.
  <!-- pop-hash: player_live_test.go sha256=69be077d33f9e697f4223e3ef92887001b88c1388d1d4f9f32acd0ad3102dead -->
- Language changes flow through `applyLanguage()`; keep `internal/search.SetTexts()` in sync when adding new search error strings.
  <!-- pop-hash: setup.go sha256=48bd036cdfff241e5aaeaca9691aa473606e459a79c6988bd8a95d86e41af8a7 -->
- Theme changes rebuild `HelpView` because it bakes colors at construction time.
- Do **not** add direct database, network or filesystem I/O in event handlers; delegate to `internal/search` or `internal/config`.
- Thumbnail fetches run in background goroutines and must queue UI updates through `app.QueueUpdateDraw()`.
- Thumbnail delivery goes through `fetchListThumbnail` (`thumbnail.go`) and the URL-guarded `SetThumbnail`/`SetKittyThumbnail` setters; any new fetch call site must keep the stale-page URL guard.
- Kitty sink (`kitty.go`): APC escapes are emitted only from the tview main loop (`SetAfterDrawFunc` sync, `SetBeforeDrawFunc` resize invalidation, queued updates) or after `Run()` returns — never from background goroutines. Transmission sends the PNG derived by `GetThumbnailPNGPath` (`a=t`, transmit-only), never the cached JPEG — the protocol accepts RGB/RGBA/PNG only. Every placement needs a matching delete on scroll/page/resize/modal/exit; blank placeholder boxes own the covered cells so tcell keeps painting them.
- `CustomList` indexes are local to the current page; account for `pagination.GetPageItems()` offsets when mapping to `tracks`.
- Do **not** import `internal/ui/components/` into the root UI files without updating this contract; components are not yet covered by a child contract.
- State restoration happens asynchronously after `NewSimpleApp()` returns; do **not** assume the playlist is populated during construction.

## Related contracts

- `../search/AGENTS.md` — follow when changing `yt-dlp` search calls or the error strings passed to `search.SetTexts()`.
- `../config/AGENTS.md` — follow when reading/writing config or session state from the UI.
- `../../pop/specs/ui-thumbnails.md` — follow when changing thumbnail rendering modes, sinks or the Kitty placement lifecycle.
