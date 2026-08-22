package ui

import (
	"encoding/base64"
	"os"
	"strings"
	"testing"
)

// captureStdout redirects os.Stdout for the duration of fn and returns
// everything written to it.
func captureStdout(t *testing.T, fn func()) string {
	t.Helper()
	orig := os.Stdout
	r, w, err := os.Pipe()
	if err != nil {
		t.Fatal(err)
	}
	os.Stdout = w
	fn()
	_ = w.Close()
	os.Stdout = orig

	buf := make([]byte, 4096)
	n, _ := r.Read(buf)
	_ = r.Close()
	return string(buf[:n])
}

func TestWriteOSC52EmitsCorrectSequence(t *testing.T) {
	text := "https://example.invalid/watch?v=abc123"

	out := captureStdout(t, func() {
		if err := writeOSC52(text); err != nil {
			t.Fatalf("writeOSC52: %v", err)
		}
	})

	wantPrefix := "\x1b]52;c;"
	wantSuffix := "\x07"
	if !strings.HasPrefix(out, wantPrefix) || !strings.HasSuffix(out, wantSuffix) {
		t.Fatalf("OSC52 sequence malformed: %q", out)
	}

	encoded := strings.TrimSuffix(strings.TrimPrefix(out, wantPrefix), wantSuffix)
	decoded, err := base64.StdEncoding.DecodeString(encoded)
	if err != nil {
		t.Fatalf("payload is not valid base64: %v", err)
	}
	if string(decoded) != text {
		t.Fatalf("decoded payload = %q, want %q", decoded, text)
	}
}

// TestCopyToClipboardFallsBackPastFailingTool ensures a clipboard tool that
// exists on PATH but fails to run (cmd.Run() != nil) does not abort the
// whole copy — the next tool in the list must still be tried.
func TestCopyToClipboardFallsBackPastFailingTool(t *testing.T) {
	binDir := t.TempDir()

	writeShim := func(name, body string) {
		path := binDir + string(os.PathSeparator) + name
		if err := os.WriteFile(path, []byte(body), 0o755); err != nil {
			t.Fatal(err)
		}
	}

	// wl-copy: exists but always fails (simulates e.g. running under X11
	// without a Wayland compositor).
	writeShim("wl-copy", "#!/bin/sh\nexit 1\n")
	// xclip: succeeds, recording that it was invoked.
	marker := binDir + string(os.PathSeparator) + "xclip-called"
	writeShim("xclip", "#!/bin/sh\ncat > /dev/null\ntouch "+marker+"\nexit 0\n")

	t.Setenv("PATH", binDir+string(os.PathListSeparator)+os.Getenv("PATH"))

	if err := copyToClipboard("hello"); err != nil {
		t.Fatalf("copyToClipboard: %v", err)
	}

	if _, err := os.Stat(marker); err != nil {
		t.Fatalf("xclip fallback was not invoked after wl-copy failed: %v", err)
	}
}

// TestCopyToClipboardAllToolsFailStillSucceedsViaOSC52 ensures that when
// every external tool fails, the OSC52 write (which needs no external
// dependency) is still enough for copyToClipboard to report success.
func TestCopyToClipboardAllToolsFailStillSucceedsViaOSC52(t *testing.T) {
	binDir := t.TempDir()
	writeShim := func(name string) {
		path := binDir + string(os.PathSeparator) + name
		if err := os.WriteFile(path, []byte("#!/bin/sh\nexit 1\n"), 0o755); err != nil {
			t.Fatal(err)
		}
	}
	writeShim("wl-copy")
	writeShim("xclip")
	writeShim("xsel")

	t.Setenv("PATH", binDir)

	out := captureStdout(t, func() {
		if err := copyToClipboard("hello"); err != nil {
			t.Fatalf("copyToClipboard should succeed via OSC52 even if every external tool fails, got: %v", err)
		}
	})

	if !strings.HasPrefix(out, "\x1b]52;c;") {
		t.Fatalf("expected OSC52 sequence to still be written, got %q", out)
	}
}

// TestCopyToClipboardNoToolsOnPathStillWritesOSC52 ensures OSC52 alone is
// sufficient for a successful copy with zero external dependencies on PATH.
func TestCopyToClipboardNoToolsOnPathStillWritesOSC52(t *testing.T) {
	emptyDir := t.TempDir()
	t.Setenv("PATH", emptyDir)

	out := captureStdout(t, func() {
		if err := copyToClipboard("hello"); err != nil {
			t.Fatalf("copyToClipboard should succeed via OSC52 with no clipboard tools installed, got: %v", err)
		}
	})

	if !strings.HasPrefix(out, "\x1b]52;c;") {
		t.Fatalf("expected OSC52 sequence to still be written, got %q", out)
	}
}
