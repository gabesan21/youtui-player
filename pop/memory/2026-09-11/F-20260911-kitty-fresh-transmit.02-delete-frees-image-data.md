---
task: F-20260911-kitty-fresh-transmit
entry: 02-delete-frees-image-data
---

# Delete frees image data too (d=I)

Field reports show real kitty may free image data when a placement is deleted, so re-placing an old image id fails silently (`q=2` hides the error). `kittyDeletePlacement` changed from `d=p` (placement only) to `d=I` (delete image by id: placements + data). Exact by design: image ids are single-use, so each id has exactly one placement. The exit path keeps `d=A` (free everything).

## Evidence

- [[internal/ui/kitty.go]] — *`kittyDeletePlacement` and `deleteSink`*.
