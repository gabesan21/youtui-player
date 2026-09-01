---
author: agent
created: 2026-09-01
---

# YouTube search by spawning yt-dlp and parsing JSON

Origin: task 1.3.1-decisions-and-references.

Relevant code (follow when editing the corresponding area):
- [[internal/search/invidious.go|invidious.go]] — follow when changing search/playlist/detail extraction
- [[internal/search/texts.go|texts.go]] — follow when changing search error messages
- [[internal/ui/health_check.go|health_check.go]] — follow when changing startup dependency checks

## Question
How does the application search YouTube and resolve video metadata?

## Observed facts

- `internal/search/invidious.go:57` defines `SearchVideos(ctx context.Context, q string, limit int) ([]Result, error)`.
- `internal/search/invidious.go:80` runs `exec.CommandContext(ctx, "yt-dlp", args...)` and streams stdout line-by-line.
- `internal/search/invidious.go:102-106` parses each line as JSON into a private `ytdlpItem` struct, skipping unparseable lines.
- The same pattern is used for playlist extraction (`GetPlaylistVideos`, line 166) and single-video details (`GetVideoDetails`, line 258), both invoking `yt-dlp` with context cancellation and JSON output templates.
- `internal/search/texts.go:22-24` and `internal/ui/i18n.go:276-278` / `i18n.go:423-425` expose user-facing strings for `YtDlpNotFound`, `YtDlpStartFailed`, and `YtDlpError`, confirming yt-dlp is a primary runtime dependency.
- `internal/ui/health_check.go:12` runs `yt-dlp --version` at startup and warns if the installed version is more than 14 days old (`daysOld > 14`, line 33).
- `internal/ui/player.go:110` passes `--script-opts=ytdl_hook-ytdl_path=yt-dlp` to mpv, so yt-dlp is also used indirectly during playback to extract stream URLs.
- Git history: `git log -S 'yt-dlp' -- internal/search/invidious.go` shows `04fb5c4 feat: url manipulation`, `4a3f99c feat: persistent language`, `14a2e7b fix: remove coments`, `af0a2b5 feat: tumbnail`, `795d5b5 feat: init repo`; `git log -S 'SearchVideos' -- internal/search/invidious.go` shows `14a2e7b` and `795d5b5`.

## Inference

The application intentionally avoids the YouTube Data API, Invidious instances, or any network client library. Instead it delegates all YouTube extraction to `yt-dlp`, which handles rate limits, format selection, and client spoofing (the recent `--extractor-args "youtube:player_client=android"` workaround in `player.go` is an example). Parsing JSON lines from a subprocess keeps the Go side stateless and lets yt-dlp's update cadence absorb YouTube breaking changes.

## Consequences

- `yt-dlp` must remain installed and relatively up to date; startup warns after 14 days.
- Search/playlist/detail logic is tightly coupled to yt-dlp's CLI output format and argument semantics.
- YouTube 403 errors (e.g., line 391 of `player.go`) are surfaced with a message telling the user to update yt-dlp.
