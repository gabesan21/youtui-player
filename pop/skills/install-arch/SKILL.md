# Skill — install-arch

- **Project:** [[pop/PROJECT|youtui-player]]
- **When to use:** you want to install the package on Arch Linux using the provided `PKGBUILD`.

## Procedure

1. Ensure you are in the repository root where `PKGBUILD` and `.SRCINFO` are located.
2. Run `makepkg -si`.
   - `makedepends = go` will be installed by `makepkg`.
   - The `PKGBUILD` downloads `youtui-player-1.3.2.tar.gz` from the upstream `IvelOt/youtui-player` release.
   - The `build()` function sets `CGO_ENABLED=0` and compiles with `-trimpath` and `-ldflags "-X main.Version=$pkgver -s -w"`.
   - The `package()` function installs `/usr/bin/youtui-player`, `/usr/share/licenses/youtui-player/LICENSE`, and `/usr/share/doc/youtui-player/README.md`.
3. Verify the install: `which youtui-player` and `youtui-player --help`.
4. Alternative local paths (not package-manager based):
   - `make install-arch` installs runtime dependencies via `pacman`; run `make build` separately to compile the binary.
   - `make install-bin` installs the freshly built binary respecting `DESTDIR`/`PREFIX` (default `/usr/local`); use `make uninstall` to remove it.

## Caveats

- **Builds upstream, not the local fork.** The `PKGBUILD` `source=` downloads the upstream `IvelOt/youtui-player` v1.3.2 tarball, so `makepkg -si` builds and installs upstream, not this fork's working tree. Adapting the package to the fork is Epoch 2 scope.
- **ffmpeg is missing from PKGBUILD depends.** `depends = ('mpv' 'yt-dlp' 'socat')` does not list `ffmpeg`, although `make check-deps` requires it for downloads. Install `ffmpeg` manually if you use the download/playback features that need it.
- **Never published to AUR.** This fork is personal and will not be published to the AUR; the `PKGBUILD` exists only as a local install path.
- **`.SRCINFO` is in sync with `PKGBUILD`.** If you ever edit `PKGBUILD`, regenerate `.SRCINFO` with `makepkg --printsrcinfo > .SRCINFO` before installing.

## Example

```bash
# From the repo root
makepkg -si

# Or install dependencies and build locally without a package
make install-arch
make build

# Or install the locally built binary directly
make install-bin
make uninstall
```
