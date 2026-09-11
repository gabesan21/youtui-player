# Kitty thumbnails — technical recon

- **Date:** 2026-09-10 · **Status:** delivered (in-repo recon, no external deep research needed)
- **Feeds:** task [[M-1.1-kitty-thumbnails]] — *follow before planning or executing it*.

## Question

How to render thumbnails as real images in terminals supporting the [Kitty graphics protocol](https://sw.kovidgoyal.net/kitty/graphics-protocol/), keeping the current pixelated rendering as fallback.

## Current pipeline (evidence)

- Thumbnail URLs synthesized from video id (`internal/search/invidious.go:121-124`); cached at `$XDG_CACHE_HOME/youtui-player/thumbnails/md5(url).jpg` (`internal/ui/thumbnail.go:22-52`).
- **Cache downsizes to max 100×100 px JPEG q90** (`internal/ui/thumbnail.go:123-136`) — too small for a good real-image rendering; the cap must be raised or removed.
- Rendering is fully delegated to `tview.Image` (`internal/ui/custom_list.go:85-87`): block-element glyphs + truecolor via `screen.SetContent()` inside tview's draw pass. No app-level renderer exists.
- Layout: list rows are FlexColumn with a fixed **20-col thumbnail** and `itemHeight = 3` rows (`custom_list.go:97-100,142`); "now playing" box has a 20-col `tview.Image` (`setup.go:90-113`). `detailsThumb`/`detailsView` (`app.go:65-66`) are dead code.
- No terminal capability detection anywhere (no `TERM`/`KITTY_WINDOW_ID` checks).
- Fetch pattern: background goroutine + `QueueUpdateDraw` at 6 call sites (`search.go:223-232`, `app.go:275-284,303-312`, `playlist.go:27-36,70-79,127-136`, `details.go:9-18`). Signatures can stay; only the sink changes. Known hazard: goroutines capture `idx` at spawn; page change can write stale images.

## Kitty protocol essentials

- Images transmitted via APC sequences (`ESC_G ... ESC \`); placement accepts **cell coordinates** (`c=20, r=3`) — no cell-pixel geometry query needed.
- **File transmission (`a=T, t=f`)** reads the image from a local path — our cache files can be sent as-is, no base64.
- Placements are **terminal-stateful** (IDs, explicit delete via `a=d`), unlike tcell cells — scroll/page/resize/exit must delete them.
- z-index: negative values draw **below text**; below `INT32_MIN/2` also below non-default cell backgrounds.
- Unicode placeholders (what yazi uses) make images scroll with text and work inside tmux — robust but complex; out of scope for the first iteration.

## The tcell/tview constraint (verified in module source)

- `tview.Application.draw()` (`application.go:680-725`): `screen.Clear()` every cycle → `root.Draw(screen)` → `afterDraw(screen)` → `screen.Show()`. **`SetAfterDrawFunc` runs before the tcell flush**, so Kitty escapes emitted there land before the repaint.
- Consequence: the image primitive must draw **blank cells** (spaces) in its area so tcell owns them, and Kitty escapes must be emitted so they survive the flush — either in `afterDraw` (image lives in a separate terminal layer; repaint of spaces doesn't erase it — validate empirically) or via a `tcell.Screen` decorator whose `Show()` emits placements after the real flush. Raw output precedent: `writeOSC52()` writes to `os.Stdout` (`internal/ui/clipboard.go:15-19`).

## Decisions from the recon

1. **Hand-rolled protocol subset** (transmit file, place with `c/r`, delete by ID) over libraries: [rasterm](https://github.com/BourgeoisBear/rasterm)/[kittyimg](https://github.com/dolmen-go/kittyimg) target print-and-exit, not managed placements in a TUI. No new dependencies.
2. **Detection:** `TERM=xterm-kitty` / `KITTY_WINDOW_ID`, plus a `[ui] image_mode = auto|kitty|blocks` config toggle; `$TMUX` disables image mode (no passthrough without Unicode placeholders) → fallback.
3. **Fallback stays the current `tview.Image`** pixelated path, selected per terminal capability.
4. **Spike first** (acceptance risk): validate flush ordering, z-index and resize behavior on the real Kitty with a minimal primitive on the "now playing" box before scaling to the list.

## Open risks

- Empirical: z-index/repaint interplay and escape ordering vs `screen.Show()` — resolved by the spike, not by reading.
- Stale-placement race on page change mirrors the existing stale-thumbnail race; fix together.
- `detailsThumb` dead code: ignore or wire, decide in planning.
