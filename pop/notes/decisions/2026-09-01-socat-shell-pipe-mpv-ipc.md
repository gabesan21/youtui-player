---
author: agent
created: 2026-09-01
---

# mpv IPC via `--input-ipc-server` Unix socket and socat shell pipes

Origin: task 1.3.1-decisions-and-references.

Relevant code (follow when editing the corresponding area):
- [[internal/ui/player.go|player.go]] — follow when changing playback control
- [[internal/ui/progress.go|progress.go]] — follow when changing progress polling
- [[internal/ui/i18n.go|i18n.go]] — follow when adding playback-related user strings

## Question
How does the application control mpv and read playback progress?

## Observed facts

- `internal/ui/player.go:106` creates a per-track Unix socket path: `socketPath := filepath.Join(os.TempDir(), fmt.Sprintf("mpv-socket-%d", time.Now().UnixNano()))`.
- `internal/ui/player.go:108-114` launches mpv with `--input-ipc-server=<socketPath>` and `--script-opts=ytdl_hook-ytdl_path=yt-dlp`.
- `internal/ui/player.go:418` toggles pause by shelling out: `exec.Command("sh", "-c", fmt.Sprintf("echo '{ \"command\": [\"cycle\", \"pause\"] }' | socat - \"%s\" 2>&1", socket))`.
- `internal/ui/player.go:609` seeks with another socat shell pipe: `echo '{ "command": ["seek", %g, "relative"] }' | socat - "%s" 2>&1`.
- `internal/ui/progress.go:52` polls current position: `echo '{ "command": ["get_property", "time-pos"] }' | socat - UNIX-CONNECT:%s ...`.
- `internal/ui/progress.go:60` polls duration: `echo '{ "command": ["get_property", "duration"] }' | socat - UNIX-CONNECT:%s ...`.
- `internal/ui/i18n.go:144-145` and `i18n.go:439-440` / `i18n.go:292-293` contain user-visible strings for `socatNotInstalled` and `socatCmdNotFound`, confirming socat is a hard runtime dependency for IPC.
- The same pattern appears twice in `player.go` (`playTrackSimple` around line 86 and a second near-identical function around line 289), both using the same socket + socat mechanism.
- Git history: `git log -S 'socat' -- internal/ui/player.go` shows `f60bd7a fix: resize visual bug`, `d278a77 fix: shufle mode`, and `2d7ec81 refactor: break in sections`; `git log -S 'input-ipc-server' -- internal/ui/player.go` shows `2d7ec81` as the earliest commit touching the mechanism in the current tree.

## Inference

The author deliberately avoided a Go mpv binding or libmpv integration and instead uses mpv's built-in JSON IPC over a Unix socket. `socat` is used as a lightweight bridge because it can speak the mpv JSON IPC line protocol without adding a Go dependency or custom socket client. This keeps the playback backend decoupled from the TUI process and matches the project's general pattern of shelling out to CLI tools (`mpv`, `yt-dlp`, `ffmpeg`, `socat`).

## Consequences

- `socat` must remain a runtime dependency; missing socat degrades pause/seek/progress features.
- Any replacement must implement the same JSON IPC over Unix socket contract or refactor playback control into a Go socket client.
- Progress polling is inherently fragile because it parses shell pipeline output with `grep`/`cut`; changes should preserve the current format or move to a structured reader.
