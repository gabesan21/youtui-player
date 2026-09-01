# youtui-player

- **Status:** in progress
- **Priority:** medium
- **Created on:** 2026-09-01
- **Roadmap:** [[pop/ROADMAP|Roadmap]]

## Goal

A terminal YouTube player in Go — search, play, download and manage playlists without leaving the shell — that is reliable and maintainable under the PoP harness.

## Context

Personal fork of Levi Renato's (IvelOt) YouTube TUI, maintained at `gabesan21/youtui-player` for personal use — **never published to the AUR** ([[pop/notes/decisions/2026-09-01-personal-fork|decision]]). Recon at import time (2026-09-01):

- Go 1.24 TUI, ~5.8k LOC, built on tview/tcell.
- Search via `yt-dlp` subprocess — `internal/search/invidious.go` is a stale filename; there is no Invidious integration.
- Playback via `mpv`, controlled through a socat-based IPC socket.
- Downloads via `yt-dlp` + `ffmpeg` (MP3/MP4).
- Config in TOML at `~/.config/youtui-player/youtui.conf`; session state as JSON under the XDG state directory.
- i18n PT-BR/EN; 4 Catppuccin themes + a Terminal theme + custom TOML themes.
- No CI; `PKGBUILD` inherited from upstream — local Arch install only; AUR publication flows are removed in [[pop/roadmap/2-fork-adaptation|Epoch 2]].

## Folder structure

Standard anatomy — no deviations to list. The project content is the Go code directly at the root: `main.go`, `internal/`, `Makefile`, `PKGBUILD`, plus the other module files. All the PoP harness lives in `pop/`; worktrees of tasks in execution live in `pop/worktrees/` (gitignored).

## Agent harness

Project-specific rules for agents working on this project:

- **Type and repositories:** declared in the [[AGENTS|project AGENTS]] — `uni-repo`; repository `github.com/gabesan21/youtui-player`, PR branch `main`.
- **Worktree per task:** yes (default).
- **Tools and restrictions:** `make build`, `make fmt`, `make vet`, `make test` — format, vet and test before closing any code task.
- **Tasks critical by default?** no.
- **Skills:** none yet in `pop/skills/` — Epoch 1 (Organization) creates them.

## Related projects

None.

## Decisions

- **2026-09-01:** project imported into the PoP as `uni-repo`; Epoch 1 (Organization) gate active — no content changes until it completes.
- **2026-09-01:** personal fork, never published to the AUR; old-repo references and AUR flows are removed in Epoch 2 — [[pop/notes/decisions/2026-09-01-personal-fork|note]].
- **2026-09-01:** Epoch 1 (Organization) completed — imported-project gate lifted; content changes to the project are now allowed.
