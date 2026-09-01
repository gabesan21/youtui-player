# internal/config — persistence and locale defaults

> Trigger: edit this contract before changing TOML config, JSON session state, XDG path resolution or locale detection.

- **Never** persist secrets, tokens or credentials in `PlayerState` or `Config`; this application has none.
- `detectDefaultLanguage()` falls back to Portuguese (`pt`), not English (`en`).
  <!-- pop-hash: config.go sha256=c65159bf606e89b0b3b7eb5c88395ff64c96fa0da54259dc6c3a6dbfc3c9d3d5 -->
- If you add a config field, add the corresponding default in `LoadConfig()` and decide whether it belongs in `Config` or `PlayerState`.
- `SaveState()` overwrites `~/.local/state/youtui-player/state.json`; do **not** keep backups or rotations here.
  <!-- pop-hash: state.go sha256=c9df1514e616aa452926ea5c828cb8b7840a73a6dc751c7cd82042e5007e7329 -->
- XDG env vars are optional; hardcoded fallbacks live in this package and must mirror the values documented in the root `AGENTS.md`.
- Do **not** import `internal/ui` or `internal/search` here; config is a leaf package.
- Normalize language codes to `en` or `pt` only; reject/unknown values map to `pt`.
- TOML keys use snake_case; keep `[theme]`, `[ui]`, `[playback]` and `[download]` sections stable to avoid breaking existing user configs.
- State restoration clamps `CurrentTrackIdx` to playlist bounds; preserve that guard for any new persisted indexes.
- `GetStatePath()` and `GetConfigPath()` are the single sources of truth for their respective file locations.

## Related contracts

- `../ui/AGENTS.md` — follow when the UI reads config at startup or writes config on language/theme changes.
