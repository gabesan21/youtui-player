package ui

import (
	"os/exec"
	"strings"
	"testing"
	"time"
)

// TestBuildYtdlFormatIncludesPlayerClientArg is a fast, offline check that
// every mpv invocation path carries ytdlPlayerClientArg, so playback goes
// through yt-dlp's Android client instead of the web/ios clients that now
// require a PO Token and return HTTP 403 Forbidden.
func TestYtdlPlayerClientArgValue(t *testing.T) {
	want := "--ytdl-raw-options=extractor-args=youtube:player_client=android"
	if ytdlPlayerClientArg != want {
		t.Fatalf("ytdlPlayerClientArg = %q, want %q", ytdlPlayerClientArg, want)
	}
}

// TestMpvPlaysLiveVideoWithAndroidClient is a real integration test: it
// shells out to mpv exactly the way playTrackSimple does (ytdl-hook +
// ytdlPlayerClientArg) against a real, known-stable YouTube video and
// verifies mpv can extract and start the stream without an HTTP 403 error.
// It requires network access and the mpv/yt-dlp/ffmpeg binaries; it is
// skipped when they are unavailable so `go test ./...` stays green offline.
func TestMpvPlaysLiveVideoWithAndroidClient(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping live network integration test in -short mode")
	}
	for _, bin := range []string{"mpv", "yt-dlp", "ffmpeg"} {
		if _, err := exec.LookPath(bin); err != nil {
			t.Skipf("%s not installed, skipping live integration test", bin)
		}
	}

	const testURL = "https://www.youtube.com/watch?v=ZZ5LpwO-An4"

	args := []string{
		"--no-terminal",
		"--script-opts=ytdl_hook-ytdl_path=yt-dlp",
		ytdlPlayerClientArg,
		"--no-video",
		"--ytdl-format=bestaudio/best",
		"--frames=1",
		testURL,
	}

	cmd := exec.Command("mpv", args...)
	var out strings.Builder
	cmd.Stdout = &out
	cmd.Stderr = &out

	done := make(chan error, 1)
	if err := cmd.Start(); err != nil {
		t.Fatalf("failed to start mpv: %v", err)
	}
	go func() { done <- cmd.Wait() }()

	select {
	case err := <-done:
		output := out.String()
		if strings.Contains(output, "403") || strings.Contains(output, "HTTP error 403") {
			t.Fatalf("mpv reported HTTP 403 Forbidden with android client args; output:\n%s", output)
		}
		if err != nil {
			if exitErr, ok := err.(*exec.ExitError); ok && exitErr.ExitCode() == 2 {
				t.Fatalf("mpv exited with code 2 (playback failure); output:\n%s", output)
			}
			t.Fatalf("mpv failed: %v; output:\n%s", err, output)
		}
	case <-time.After(60 * time.Second):
		_ = cmd.Process.Kill()
		t.Fatal("mpv did not finish within 60s")
	}
}
