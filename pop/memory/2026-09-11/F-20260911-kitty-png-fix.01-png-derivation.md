---
task: F-20260911-kitty-png-fix
entry: 01-png-derivation
---

# PNG derivation for the Kitty sink

The kitty protocol accepts only RGB, RGBA and PNG pixel data (`f=100` = PNG); the M-1.1 implementation transmitted the JPEG cache files via `t=f` and kitty rejected them silently (`q=2` suppresses the error), leaving every thumbnail area blank. `GetThumbnailPNGPath` in `internal/ui/thumbnail.go` now derives `<cache>.png` (mtime-guarded re-encode via std-lib `image/png`) and both kitty call sites transmit that path; the JPEG cache stays the single source for the blocks sink.

## Evidence

- [[internal/ui/thumbnail.go]] — *the derivation and the two sink call sites*.
- [[pop/specs/ui-thumbnails|ui-thumbnails]] — *Interfaces updated to record the PNG-only constraint*.
