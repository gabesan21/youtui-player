---
task: D-20260905-mpv-exit-status-2
project: youtui-player
started: 2026-09-05
finished: 2026-09-05
commit: 5364f794a43f804a6382a2047f3839022f4fd80b
pr:
authorization: direct fix (user command, no-kanban route)
---

# D-20260905-mpv-exit-status-2 — mpv exit status 2 on playback

- **Delivery:** playback works again — the yt-dlp `player_client=android` pin was removed from every mpv invocation.
- **Verification:** reproduced live (with the pin: exit 2; without: stream starts); `make build`/`fmt`/`vet`/`test` green, live test in 12.9s.
- **Contract impact:** DOX root rail gained the "never pin a yt-dlp player_client" rule; `internal/ui/AGENTS.md` pop-hash refreshed.

## Entries

- [[D-20260905-mpv-exit-status-2.01-player-client-pin-removed]] — root cause, fix and lesson.

## Links

- **Commit:** 5364f794a43f804a6382a2047f3839022f4fd80b — *follow to inspect the diff*.
