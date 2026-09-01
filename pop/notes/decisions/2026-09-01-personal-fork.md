---
author: user
created: 2026-09-01
---

# Personal fork — never published to AUR

Recorded at import (conversation, 2026-09-01).

`gabesan21/youtui-player` is a **personal fork** of `IvelOt/youtui-player` (Levi Renato). It will be modified for personal needs and will **never** be published as an AUR release.

Consequences:

- The Go module path and `PKGBUILD` still point to `IvelOt/youtui-player` — removed in [[pop/roadmap/2-fork-adaptation|Epoch 2 (Fork adaptation)]]; the README keeps the single upstream reference, stating the fork reason.
- AUR publication flows (`.SRCINFO`, AUR badge/references) are removed in Epoch 2; the `PKGBUILD` remains only as a local Arch install path (`makepkg -si`).
- No release/versioning strategy is needed — personal use only.
