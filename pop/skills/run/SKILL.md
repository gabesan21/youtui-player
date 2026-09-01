# Skill — run

- **Project:** [[pop/PROJECT|youtui-player]]
- **When to use:** you want to build and immediately run the application locally.

## Procedure

1. Ensure you are in the repository root.
2. Verify runtime dependencies with `make check-deps`.
   - The check reports presence/absence of: `mpv`, `yt-dlp`, `socat`, `ffmpeg`.
   - Install missing binaries first (for Arch, see the `install-arch` skill).
3. Copy or reference the example config from `config-exemples/youtui.conf.example` to `~/.config/youtui-player/youtui.conf`.
4. Optional: review `.env.example` for optional XDG/locale environment overrides.
   - `XDG_CONFIG_HOME`, `XDG_STATE_HOME`, `XDG_CACHE_HOME`, `XDG_DATA_HOME`, `XDG_DOWNLOAD_DIR`
   - `LANG`, `LC_ALL`, `LC_MESSAGES`
   - None of these are required or secret.
5. Run `make run`.
   - This first runs `make build` (which runs `make deps`), then executes `./youtui-player`.

## Caveats

- `make run` will rebuild the binary every time; if the binary is already fresh and you only want to run it, invoke `./youtui-player` directly.
- `make check-deps` only prints status lines; it does not install anything.
- The config path is hardcoded to `~/.config/youtui-player/youtui.conf` unless overridden by `XDG_CONFIG_HOME`.
- The example config sets defaults such as `language = "en"`, `default_mode = "audio"`, and `dir = "~/Music/youtui`.

## Example

```bash
make check-deps
mkdir -p ~/.config/youtui-player
cp config-exemples/youtui.conf.example ~/.config/youtui-player/youtui.conf
make run
```
