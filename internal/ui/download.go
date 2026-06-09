package ui

import (
	"bufio"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	"github.com/IvelOt/youtui-player/internal/config"
	"github.com/rivo/tview"
)

// dlProgressPrefix marks lines emitted by yt-dlp's --progress-template so they
// can be told apart from ordinary output on the shared stdout/stderr stream.
const dlProgressPrefix = "YTDLPCT:"

// renderProgressBar turns a yt-dlp percent string (e.g. " 45.2%") into a fixed
// width bar. Returns "" if the value can't be parsed.
func renderProgressBar(pct string) string {
	const width = 20
	v, err := strconv.ParseFloat(strings.TrimSuffix(strings.TrimSpace(pct), "%"), 64)
	if err != nil {
		return ""
	}
	filled := int(v / 100 * width)
	if filled < 0 {
		filled = 0
	}
	if filled > width {
		filled = width
	}
	return "[" + strings.Repeat("█", filled) + strings.Repeat("░", width-filled) + "]"
}

func resolveDownloadDir(cfg *config.Config) string {
	dir := cfg.Download.Dir
	if dir == "" {
		if xdg := os.Getenv("XDG_DOWNLOAD_DIR"); xdg != "" {
			return xdg
		}
		if homeDir, err := os.UserHomeDir(); err == nil {
			return filepath.Join(homeDir, "Downloads")
		}
		return "."
	}
	if strings.HasPrefix(dir, "~/") {
		if homeDir, err := os.UserHomeDir(); err == nil {
			return filepath.Join(homeDir, dir[2:])
		}
	}
	return dir
}

func buildDownloadFormat(mode PlayMode, quality, codec string) string {
	if mode == ModeAudio {
		// Source stream for audio; it is re-encoded to MP3 by ffmpeg afterwards.
		return "bestaudio/best"
	}
	// TCT is a playback-only mode; fall back to 360p for downloads.
	if quality == "tct" {
		quality = "360"
	}
	return buildYtdlFormat(quality, codec)
}

func (a *SimpleApp) downloadTrack(track Track) {
	cfg, _ := config.LoadConfig()
	dir := resolveDownloadDir(cfg)
	if err := os.MkdirAll(dir, 0o755); err != nil {
		dir = os.TempDir()
	}

	a.app.QueueUpdateDraw(func() {
		a.setStatusf(a.theme.Sapphire, "⬇ "+a.strings.Downloading, track.Title)
	})

	a.mu.Lock()
	playMode := a.playMode
	quality := a.videoQuality
	codec := a.videoCodec
	a.mu.Unlock()

	args := []string{
		"--no-warnings",
		"--newline",
		"--color", "never",
		"--progress-template", "download:" + dlProgressPrefix + "%(progress._percent_str)s",
		"-o", filepath.Join(dir, "%(title)s.%(ext)s"),
		"--format", buildDownloadFormat(playMode, quality, codec),
	}
	if playMode == ModeAudio {
		// Extract audio to MP3 (requires ffmpeg).
		args = append(args, "-x", "--audio-format", "mp3", "--audio-quality", "0")
	} else {
		// Default video container to MP4 (remux/merge requires ffmpeg).
		args = append(args, "--merge-output-format", "mp4")
	}
	args = append(args, track.URL)

	cmd := exec.Command("yt-dlp", args...)
	pr, pw := io.Pipe()
	cmd.Stdout = pw
	cmd.Stderr = pw

	if err := cmd.Start(); err != nil {
		_ = pw.Close()
		a.app.QueueUpdateDraw(func() {
			a.setStatusf(a.theme.Red, "❌ "+a.strings.DownloadError, err)
		})
		return
	}

	// Stream output: parse progress lines into a live bar, keep the tail of
	// everything else for error reporting.
	var tail []string
	done := make(chan struct{})
	go func() {
		defer close(done)
		sc := bufio.NewScanner(pr)
		sc.Buffer(make([]byte, 0, 64*1024), 1024*1024)
		var lastPct string
		var lastUpdate time.Time
		for sc.Scan() {
			line := strings.TrimSpace(sc.Text())
			if line == "" {
				continue
			}
			if idx := strings.Index(line, dlProgressPrefix); idx >= 0 {
				pct := strings.TrimSpace(line[idx+len(dlProgressPrefix):])
				if pct == lastPct || time.Since(lastUpdate) < 200*time.Millisecond {
					continue
				}
				lastPct = pct
				lastUpdate = time.Now()
				bar := renderProgressBar(pct)
				a.app.QueueUpdateDraw(func() {
					a.setStatus(a.theme.Sapphire, fmt.Sprintf("⬇ %s  %s %s", track.Title, bar, pct))
				})
				continue
			}
			tail = append(tail, line)
			if len(tail) > 8 {
				tail = tail[1:]
			}
		}
	}()

	err := cmd.Wait()
	_ = pw.Close()
	<-done

	if err != nil {
		detail := mpvErrorDetail(strings.Join(tail, "\n"))
		a.app.QueueUpdateDraw(func() {
			if detail != "" {
				a.setStatusf(a.theme.Red, "❌ "+a.strings.DownloadError, detail)
			} else {
				a.setStatusf(a.theme.Red, "❌ "+a.strings.DownloadError, err)
			}
		})
		return
	}

	a.app.QueueUpdateDraw(func() {
		a.setStatusf(a.theme.Green, "✓ "+a.strings.DownloadComplete, track.Title)
	})
}

// getContextTrack returns the most relevant track for the current focus:
// playing track > focused list item.
func (a *SimpleApp) getContextTrack(focused tview.Primitive) *Track {
	a.mu.Lock()
	if a.isPlaying && a.currentTrack >= 0 && a.currentTrack < len(a.playlistTracks) {
		t := a.playlistTracks[a.currentTrack]
		a.mu.Unlock()
		return &t
	}
	a.mu.Unlock()

	switch focused {
	case a.searchResults.Flex:
		return a.searchResults.GetCurrentTrack()
	case a.playlist.Flex:
		idx := a.playlist.GetCurrentItem()
		a.mu.Lock()
		defer a.mu.Unlock()
		if idx >= 0 && idx < len(a.playlistTracks) {
			t := a.playlistTracks[idx]
			return &t
		}
	}
	return nil
}

// saveURLToFile writes the URL to ~/.local/share/youtui-player/last_url.txt
// and returns the file path.
func (a *SimpleApp) saveURLToFile(url string) (string, error) {
	baseDir := os.Getenv("XDG_DATA_HOME")
	if baseDir == "" {
		homeDir, err := os.UserHomeDir()
		if err != nil {
			return "", err
		}
		baseDir = filepath.Join(homeDir, ".local", "share")
	}

	dir := filepath.Join(baseDir, "youtui-player")
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return "", err
	}

	filePath := filepath.Join(dir, "last_url.txt")
	return filePath, os.WriteFile(filePath, []byte(url+"\n"), 0o644)
}

// showURLModal displays the track URL in a modal so the user can copy it
// with tmux, and also saves it to last_url.txt.
func (a *SimpleApp) showURLModal(focused tview.Primitive) {
	var url string

	a.mu.Lock()
	if a.isPlaying && a.currentTrack >= 0 && a.currentTrack < len(a.playlistTracks) {
		url = a.playlistTracks[a.currentTrack].URL
	}
	a.mu.Unlock()

	if url == "" {
		switch focused {
		case a.searchResults.Flex:
			if t := a.searchResults.GetCurrentTrack(); t != nil {
				url = t.URL
			}
		case a.playlist.Flex:
			idx := a.playlist.GetCurrentItem()
			a.mu.Lock()
			if idx >= 0 && idx < len(a.playlistTracks) {
				url = a.playlistTracks[idx].URL
			}
			a.mu.Unlock()
		}
	}

	if url == "" {
		a.app.QueueUpdateDraw(func() {
			a.setStatus(a.theme.Yellow, "⚠ "+a.strings.NoTrackSelected)
		})
		return
	}

	savedPath, _ := a.saveURLToFile(url)

	a.app.QueueUpdateDraw(func() {
		a.prevFocused = focused
		a.inModal = true

		text := fmt.Sprintf("%s\n\n%s", a.strings.URLModalTitle, url)
		if savedPath != "" {
			text += "\n\n" + fmt.Sprintf(a.strings.URLSaved, savedPath)
		}

		modal := tview.NewModal().
			SetText(text).
			AddButtons([]string{a.strings.Close}).
			SetDoneFunc(func(_ int, _ string) {
				a.inModal = false
				a.app.SetRoot(a.getMainLayout(), true)
				if a.prevFocused != nil {
					a.app.SetFocus(a.prevFocused)
				}
			})

		a.app.SetRoot(modal, true)
	})
}
