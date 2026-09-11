---
task: F-20260911-kitty-png-fix
entry: 02-transmit-only-and-retransmit
---

# Transmit-only action and re-transmit on invalidate

`kittyTransmitFile` used `a=T`, which displays the image at the cursor at transmit time; it now emits `a=t` (transmit-only), with display exclusively via the `a=p` placement. `Invalidate` also resets the transmitted registry so the next Sync re-transmits after delete-all — field reports show real terminals may free image data when placements are deleted, so re-placement without re-transmission is unreliable. tcell's per-frame Clear() was ruled out as a factor: it is a back-buffer Fill, not ESC[2J.

## Evidence

- [[internal/ui/kitty.go]] — *the emitter and the renderer lifecycle*.
