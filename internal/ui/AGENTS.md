# internal/ui — TUI layer and concurrency rules

> Trigger: edit this contract before changing widgets, event handlers, playback goroutines, theme/language wiring or state restoration.

- **Never** mutate tview primitives from background goroutines; always use `app.QueueUpdateDraw()`.
  <!-- pop-hash: app.go sha256=52bb0b3dc0ed6d0c4c0205ece35b193a29cf295b8e9b5c1264da0a88d886ab83 -->
- `SimpleApp.mu` guards shared state; lock before accessing `tracks`, `playlistTracks`, `currentTrack` or playback flags from any goroutine.
- `player_live_test.go` contains a live network test skipped under `-short`; do **not** make it required in `make test` or CI.
  <!-- pop-hash: player_live_test.go sha256=69be077d33f9e697f4223e3ef92887001b88c1388d1d4f9f32acd0ad3102dead -->
- Language changes flow through `applyLanguage()`; keep `internal/search.SetTexts()` in sync when adding new search error strings.
  <!-- pop-hash: setup.go sha256=d9a311a7118e1c9ad19856f3bb5b8f895e13d32e22195913e7fb36b7d3147c6b -->
- Theme changes rebuild `HelpView` because it bakes colors at construction time.
- Do **not** add direct database, network or filesystem I/O in event handlers; delegate to `internal/search` or `internal/config`.
- Thumbnail fetches run in background goroutines and must queue UI updates through `app.QueueUpdateDraw()`.
- Thumbnail delivery goes through `fetchListThumbnail` (`thumbnail.go`) and the URL-guarded `SetThumbnail`/`SetKittyThumbnail` setters; any new fetch call site must keep the stale-page URL guard.
- Kitty sink (`kitty.go`): APC escapes are emitted only from the tview main loop (`SetAfterDrawFunc` sync, `SetBeforeDrawFunc` resize invalidation, queued updates) or after `Run()` returns — never from background goroutines. Transmission sends the PNG derived by `GetThumbnailPNG` (`a=t`, transmit-only), never the cached JPEG — the protocol accepts RGB/RGBA/PNG only. Placements are aspect-correct (center source crop via cell pixel size) and must be clamped to the owning panel's inner rect — kitty ignores tview's cell clipping. Every placement needs a matching delete on scroll/page/resize/modal/exit; blank placeholder boxes own the covered cells so tcell keeps painting them.
- Kitty sink keys are **content-keyed** (`prefix:videoID` parsed from the `i.ytimg.com/vi/<id>/` thumbnail URL, fallback the track URL), never `prefix:index` — an index shift (scroll, delete, move, page change) must not mis-pair a placement with another track. Any spec change deletes the old placement and re-places with a **fresh placement id** (fresh transmit only when the path changes); a `renderVisibleItems` generation bump forces re-place at the next `Sync` even when a spec compares equal. `YOUTUI_KITTY_DEBUG=<path>` appends per-Sync decision logs; unset = no I/O.
- `CustomList` indexes are local to the current page; account for `pagination.GetPageItems()` offsets when mapping to `tracks`.
- Do **not** import `internal/ui/components/` into the root UI files without updating this contract; components are not yet covered by a child contract.
- State restoration happens asynchronously after `NewSimpleApp()` returns; do **not** assume the playlist is populated during construction.

## Related contracts

- `../search/AGENTS.md` — follow when changing `yt-dlp` search calls or the error strings passed to `search.SetTexts()`.
- `../config/AGENTS.md` — follow when reading/writing config or session state from the UI.
- `../../pop/specs/ui-thumbnails.md` — follow when changing thumbnail rendering modes, sinks or the Kitty placement lifecycle.
