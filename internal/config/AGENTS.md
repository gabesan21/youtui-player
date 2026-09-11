# internal/config — persistence and locale defaults

> Trigger: edit this contract before changing TOML config, JSON session state, XDG path resolution or locale detection.

- **Never** persist secrets, tokens or credentials in `PlayerState` or `Config`; this application has none.
- `detectDefaultLanguage()` falls back to Portuguese (`pt`), not English (`en`).
  <!-- pop-hash: config.go sha256=4f54fa60ed9c332d71ce8c39e1ef7ac0bb50cc02e1d076f5edba6f53b204a353 -->
- If you add a config field, add the corresponding default in `LoadConfig()` and decide whether it belongs in `Config` or `PlayerState`.
- `SaveState()` overwrites `~/.local/state/youtui-player/state.json`; do **not** keep backups or rotations here.
  <!-- pop-hash: state.go sha256=c9df1514e616aa452926ea5c828cb8b7840a73a6dc751c7cd82042e5007e7329 -->
- XDG env vars are optional; hardcoded fallbacks live in this package and must mirror the values documented in the root `AGENTS.md`.
- Do **not** import `internal/ui` or `internal/search` here; config is a leaf package.
- Normalize language codes to `en` or `pt` only; reject/unknown values map to `pt`.
- Normalize `image_mode` to `auto|kitty|blocks` via `NormalizeImageMode()`; unknown/empty values map to `auto`.
- TOML keys use snake_case; keep `[theme]`, `[ui]`, `[playback]` and `[download]` sections stable to avoid breaking existing user configs.
- State restoration clamps `CurrentTrackIdx` to playlist bounds; preserve that guard for any new persisted indexes.
- `GetStatePath()` and `GetConfigPath()` are the single sources of truth for their respective file locations.

## Related contracts

- `../ui/AGENTS.md` — follow when the UI reads config at startup or writes config on language/theme changes.
