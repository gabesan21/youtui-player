---
task: D-mpv-exit-status-2
project: youtui-player
started: 2026-09-05
finished: 2026-09-05
commit: 5364f794a43f804a6382a2047f3839022f4fd80b
pr:
authorization: direct fix (user command, no-kanban route)
---

# D-mpv-exit-status-2 — mpv exit status 2 on playback

- **Symptom:** every playback failed with `Erro mpv: exit status 2`, while plain `yt-dlp` and argument-less `mpv` worked.
- **Root cause:** `ytdlPlayerClientArg` (`--ytdl-raw-options=extractor-args=youtube:player_client=android`, `internal/ui/player.go`) — introduced to dodge HTTP 403 PO-Token errors — became the failure: YouTube now serves no streams to the Android client (yt-dlp 2026.08.18 warns "Skipping client android" and returns storyboards only), so `bestvideo+bestaudio/best` matched nothing and mpv exited 2.
- **Fix:** removed the constant and its 4 uses (`playTrackSimple()`, `playTrackDirect()`, both tct paths); yt-dlp now picks its default clients. `TestYtdlPlayerClientArgValue` deleted; `TestMpvPlaysLiveVideoWithAndroidClient` renamed to `TestMpvPlaysLiveVideo` and aligned with the new invocation.
- **Verification:** reproduced live (mpv with app args → exit 2, "Requested format is not available"; without the android arg → stream starts); `make build`/`fmt`/`vet`/`test` green, live test ran in 12.9s.
- **Contract impact:** DOX root rail gained the "never pin a yt-dlp player_client" rule; `internal/ui/AGENTS.md` pop-hash for `player_live_test.go` refreshed.
- **Lesson:** workarounds against YouTube client policy rot fast — prefer yt-dlp defaults and keep the live test as the tripwire.

## Links

- **Commit:** 5364f794a43f804a6382a2047f3839022f4fd80b.
