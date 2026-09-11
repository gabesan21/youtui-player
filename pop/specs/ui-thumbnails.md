---
id: ui-thumbnails
project: youtui-player
domain: ui
kind: contract
status: active
implementation: implemented
origin: "M-1.1-kitty-thumbnails"
created: 2026-09-10
updated: 2026-09-11
supersedes: []
superseded_by:
---

# Spec — thumbnail rendering modes (Kitty images with blocks fallback)

## Contract

How the TUI renders track thumbnails given terminal capability and user preference, and which fallback is guaranteed.

## Expected behavior

- Given `[ui] image_mode = "auto"` (the default) and a Kitty terminal (`TERM=xterm-kitty` or `KITTY_WINDOW_ID` set) outside tmux, when thumbnails load, then the search/playlist list and the "now playing" box show real images via the Kitty graphics protocol.
- Given `image_mode = "blocks"`, a non-Kitty terminal, or `$TMUX` set, when thumbnails load, then rendering is the pixelated block-element path (`tview.Image`) exactly as before the Kitty support existed.
- Given an `image_mode` value outside `auto|kitty|blocks`, when config loads, then it normalizes to `auto`.
- When the user scrolls, changes page, resizes or exits, then all Kitty placements are explicitly deleted — no leftover images on the terminal.

## Invariants

- The blocks rendering path always works and is always the fallback; Kitty support never removes or degrades it.
- No Kitty escape sequences are emitted when the blocks mode is selected.
- Kitty image placements are terminal state owned by the app: every placement has a matching delete on any layout-affecting event and on exit.
- Kitty placements are keyed by **content** (`prefix:videoID` parsed from the `i.ytimg.com/vi/<id>/` thumbnail URL, fallback the track URL), never by list index — an index shift (scroll, delete, move, page change) cannot mis-pair a placement with another track.
- A changed placement spec always deletes the old placement and re-places with a **fresh placement id** (fresh transmit when the image path changes); a re-rendered visible window (list generation bump) forces a re-place at the next sync even when a spec coincidentally compares equal.
- No new third-party dependencies for image rendering, beyond `golang.org/x/sys` (already an indirect tcell dependency, promoted to direct for the `TIOCGWINSZ` cell-geometry query).

## Interfaces

- **Input:** `[ui] image_mode` TOML key — `"auto" | "kitty" | "blocks"`, default `"auto"`; thumbnail source files from the existing on-disk cache. The kitty sink transmits a PNG derived next to each cached JPEG (`<cache>.jpg.png` via `GetThumbnailPNG`) — the Kitty protocol accepts only RGB/RGBA/PNG payloads, not JPEG; the JPEG cache remains the single source for the blocks sink.
- **Output:** real images (Kitty placements by cell coordinates) or pixelated blocks, per mode selection. Kitty placements display an aspect-correct center crop of the source image (source pixel rect `x/y/w/h` scaled into the target cells, using the terminal's cell pixel geometry) and are clamped to the inner rect of their owning panel — a partially visible row shows the corresponding partial image, never bleeding into neighboring panels.
- **Compatibility:** existing configs without `image_mode` behave as `auto`; non-Kitty terminals are unaffected.

## Errors and limits

- **Terminal without Kitty support:** blocks fallback, silently.
- **Inside tmux:** blocks fallback (no escape passthrough in this iteration).
- **Image transmission/placement failure:** the affected thumbnail degrades to its blank/blocks area without crashing or corrupting the UI.
- **Field diagnosis:** `YOUTUI_KITTY_DEBUG=<path>` appends a per-sync decision log (timestamp, desired vs live keys, deletes, places with rects); unset means a silent no-op with zero I/O.

## Conformance criteria

- [ ] Mode selection honors env detection, config toggle and tmux gate.
- [ ] Kitty mode shows real images in list and now-playing box; blocks mode is byte-identical in behavior to the pre-Kitty rendering.
- [ ] No residual placements after scroll, page change, resize or exit.

## Out of scope

- Unicode-placeholder images and tmux passthrough (possible future iteration).
- Video/terminal playback rendering (`tct` mode) — unchanged.

## Related references

- [`internal/ui/AGENTS.md`](../../internal/ui/AGENTS.md) — *follow when editing the TUI layer that implements this contract*.
- [`internal/config/AGENTS.md`](../../internal/config/AGENTS.md) — *follow when changing the `[ui]` config section*.
