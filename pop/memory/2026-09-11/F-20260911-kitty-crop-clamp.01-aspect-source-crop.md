---
task: F-20260911-kitty-crop-clamp
entry: 01-aspect-source-crop
---

# Aspect-preserving source-crop placement

Placement with `c/r` alone stretches the image into the cell rect. Kitty placement keys `x,y,w,h` select a source region scaled into `c×r`, so the sink computes the largest centered source rect matching the target aspect — cell size from TIOCGWINSZ (`golang.org/x/sys/unix`, promoted to direct dep), fallback 1:2 cells. Source dims flow from the PNG derivation (`GetThumbnailPNG` returns path+dims). Derived PNG files are unchanged: no re-encoding per aspect.

## Evidence

- [[internal/ui/kitty.go]] — *cell measurement, crop math and the placement emitter*.
- [[internal/ui/thumbnail.go]] — *GetThumbnailPNG returning path + dimensions*.
