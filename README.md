# YouTui-player

A modern YouTube player for the terminal with TUI interface.

![Go Version](https://img.shields.io/badge/go-1.24+-blue)
![License](https://img.shields.io/badge/license-MIT-blue)

## What does it do?

YouTui-player is a YouTube player that runs entirely in the terminal, allowing you to search, play and download music/videos, and manage playlists without leaving the command line. Beautiful interface with inline thumbnails, complete controls, and 5 themes (4 Catppuccin variants plus a native terminal theme).

**Key features:**

- Fast YouTube search (no API keys required)
- High-quality thumbnails in terminal
- Playlist with shuffle, repeat, and navigation
- Complete controls (play, pause, next, previous)
- Real-time progress bar
- Audio and video playback modes
- Terminal video mode (renders video as unicode art via `mpv --vo=tct`)
- Configurable video quality (Best, 360p, 480p, 720p, 1080p, Terminal)
- Configurable video codec (Any, VP9, AV1)
- Download tracks (`Ctrl+D`) — MP3 for audio, MP4 for video, with live progress and a configurable folder
- Show or save a track's URL (`Y`) — handy for copying inside tmux/SSH
- 4 Catppuccin themes + a native **Terminal** theme that inherits your terminal colors
- Real-time theme and language switching (no restart)
- Custom theme support
- Multilingual (PT-BR and EN)

## Screenshots

<img width="1917" height="1045" alt="image" src="https://github.com/user-attachments/assets/94df9e10-d1d5-4065-b668-0ae003def764" />
<img width="1903" height="1036" alt="image" src="https://github.com/user-attachments/assets/e4c9957a-c14b-4c68-9bf1-7a00e3579900" />

## Dependencies

- **Go 1.24+** - Programming language
- **mpv** - Media player
- **yt-dlp** - YouTube video extractor
- **socat** - IPC communication with mpv
- **ffmpeg** - Audio/video extraction for downloads (MP3 audio, MP4 video)
- **Nerd Font** (optional) - For beautiful icons

## Installation

### Arch Linux (AUR) — recommended

No Go required. The AUR package handles everything automatically.

```bash
# Using yay
yay -S youtui-player

# Using paru
paru -S youtui-player

# Manually
git clone https://aur.archlinux.org/youtui-player.git
cd youtui-player
makepkg -si
```

After install, make sure you have the runtime dependencies:

```bash
sudo pacman -S mpv yt-dlp socat ffmpeg
```

---

### Manual (from source)

Requires **Go 1.24+**, **mpv**, **yt-dlp**, **socat** and **ffmpeg**.

```bash
# Install runtime dependencies (Arch Linux)
sudo pacman -S mpv yt-dlp socat ffmpeg go

# Clone and build
git clone https://github.com/IvelOt/youtui-player
cd youtui-player
make build

# Run
./youtui-player

# Or install to /usr/local/bin
sudo make install-bin
```

## Main Shortcuts

| Key       | Action                          |
| --------- | ------------------------------- |
| `/`       | Search                          |
| `Enter`   | Play/Search                     |
| `a` / `A` | Add one / all to playlist       |
| `d`       | Remove from playlist            |
| `Space`   | Pause/Resume                    |
| `n` / `p` | Next/Previous                   |
| `h` / `l` | Seek -5s / +5s (player)         |
| `r`       | Repeat mode (playlist)          |
| `Ctrl+D`  | Download track (MP3/MP4)        |
| `y` / `Y` | Copy URL / show & save URL      |
| `Tab`     | Switch panels                   |
| `?`       | Full help                       |
| `Ctrl+C`  | Settings                        |
| `Ctrl+Q`  | Quit                            |
| `m`       | Toggle audio/video              |

## Downloads

Press `Ctrl+D` to download the currently playing or selected track with `yt-dlp`.
Progress is shown live in the status bar.

- **Audio mode** → extracted to **MP3** (requires `ffmpeg`)
- **Video mode** → saved in an **MP4** container, honoring the chosen quality/codec (requires `ffmpeg`)

The download folder is configured in the settings view (`Ctrl+C`). If left empty it
falls back to `$XDG_DOWNLOAD_DIR`, then `~/Downloads`. The `[download]` section of
`~/.config/youtui-player/youtui.conf` stores it:

```toml
[download]
dir = "~/Music/youtui"
```

Press `Y` to view a track's full URL in a popup (also saved to
`~/.local/share/youtui-player/last_url.txt`), useful for copying inside tmux/SSH.

## Settings

Press `Ctrl+C` to open the settings form. It lets you change, in real time:

- Language (PT-BR / EN)
- Theme
- Video quality and codec
- Download folder

Changes are saved to `~/.config/youtui-player/youtui.conf`.

## Themes

YouTui-player includes 4 Catppuccin themes plus a native terminal theme:

- 🌻 **Latte** - Elegant light mode
- 🪴 **Frappé** - Cool dark mode
- 🌺 **Macchiato** - Warm dark mode
- 🌿 **Mocha** - Deep dark mode (default)
- 🖥️ **Terminal** - Inherits your terminal's own colors

**Switch theme:** press `Ctrl+C`, then pick a theme from the dropdown — it applies
instantly, no restart needed.

**Custom theme:**
See [THEMES.md](THEMES.md) for instructions on how to create your own theme.

## Development

```bash
# Check dependencies
make check-deps

# Compile
make build

# Compile and run
make run

# Format code
make fmt

# Clean generated files
make clean
```

## License

MIT License

Copyright (c) 2025 IvelOt

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
