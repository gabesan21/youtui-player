# internal/search — yt-dlp search backend

> Trigger: edit this contract before changing `yt-dlp` invocation, `Result` shape, error-message strings or the i18n bridge.

- **Never** change `Result` field names without updating every consumer in `internal/ui/search.go` and `internal/ui/playlist.go`.
- `yt-dlp` is the only search backend; do **not** add HTTP clients, API keys or mock servers.
  <!-- pop-hash: invidious.go sha256=f297b1a57dcc598bc3ab2a7e4b8d74dd2823bdbcefda73a01dc7ddcdfef55c0f -->
- Timeouts are caller responsibility; functions here return raw `error` values and **must not** format status strings for the UI.
- `SetTexts()` is the cross-package i18n bridge from `internal/ui`; keep the `search.Texts` keys in sync with `internal/ui/i18n.go`.
  <!-- pop-hash: texts.go sha256=6c8dcddb7a17c83dc8ae742d1ad52db44989ae428a738b1f88f9144d637546b9 -->
- Default limits are 30 for search and 200 for playlists; if you change them, update pagination assumptions in `internal/ui/search.go`.
- The package default language is Portuguese (`pt`); `SetTexts()` overrides it at runtime.
- Do **not** import `internal/ui` here; the dependency direction is UI → search, never the reverse.
- If `yt-dlp` changes its JSON output shape, update `ytdlpItem` before any public function.
- Thumbnails are synthesized from video ID (`https://i.ytimg.com/vi/<id>/hqdefault.jpg`); do **not** fetch thumbnail bytes in this package.
- Do **not** run `yt-dlp` without `context.Context` cancellation support; every public entry point receives a context.

## Related contracts

- `../ui/AGENTS.md` — follow when changing search UI text or the strings passed through `SetTexts()`.
