---
task: D-20260905-mpv-exit-status-2
entry: 01-player-client-pin-removed
---

# yt-dlp player_client pin removed

Every playback failed with `exit status 2` while plain yt-dlp worked. Root cause: `ytdlPlayerClientArg` (`--ytdl-raw-options=extractor-args=youtube:player_client=android`) — added to dodge PO-Token 403s — made YouTube serve no streams (yt-dlp 2026.08.18 skips the android client), so no format matched. Fix: removed the constant and its 4 uses in `player.go`; yt-dlp picks default clients. Tests aligned. Lesson: workarounds against YouTube client policy rot fast — prefer yt-dlp defaults, keep the live test as tripwire.

## Evidence

- [[internal/ui/player.go]] — *the file where the pin lived*.
- [[internal/ui/player_live_test.go]] — *the tripwire test*.
