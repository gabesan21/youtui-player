---
task: F-20260911-kitty-fresh-transmit
entry: 01-single-use-image-ids
---

# Single-use image ids: fresh transmit on every place

The graphics protocol leaves overlapping same-z placements of the **same image id** undefined; re-place reused image ids, so a lost/raced delete kept the old frame visible — the static-thumbnails symptom. `placeSink` now allocates a new image id and emits the `a=t,t=f` transmit on EVERY placement, and the `transmitted` path→id dedup map was removed (re-transmitting a path is a tiny escape; kitty reads the file itself). Cost is one small escape per visible image per re-place.

## Evidence

- [[internal/ui/kitty.go]] — *`placeSink` and the dedup-free `transmit`*.
