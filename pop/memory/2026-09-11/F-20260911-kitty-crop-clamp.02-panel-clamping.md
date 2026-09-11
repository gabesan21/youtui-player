---
task: F-20260911-kitty-crop-clamp
entry: 02-panel-clamping
---

# Panel clamping for Kitty placements

tview clips cells when drawing, so the blocks path never leaked — but Kitty placements honor the raw `GetInnerRect` even for rows clipped by the panel border (latent bug surfaced by images). Every desired placement is now intersected with the owning canvas (list container / playerBox inner rect); fully clipped or unlaid-out rects contribute no sink, so Sync deletes stale placements, and partially visible rows map the clamped cell rect back into the source crop proportionally, mirroring tcell's cell clipping.

## Evidence

- [[internal/ui/kitty.go]] — *kittyRect.intersect and the partial-visibility math*.
- [[internal/ui/custom_list.go]] — *kittySinkSpecs clamped to the container rect*.
