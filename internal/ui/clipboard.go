package ui

import (
	"encoding/base64"
	"fmt"
	"os"
	"os/exec"
	"strings"
)

// writeOSC52 emits an OSC 52 escape sequence that asks the terminal emulator
// itself to set the system clipboard. Supported natively by most modern
// terminals (including over SSH/tmux with passthrough configured), so it
// needs no external clipboard tool at all.
func writeOSC52(text string) error {
	encoded := base64.StdEncoding.EncodeToString([]byte(text))
	_, err := fmt.Fprintf(os.Stdout, "\x1b]52;c;%s\x07", encoded)
	return err
}

func copyToClipboard(text string) error {
	osc52Err := writeOSC52(text)

	copiers := []struct {
		name string
		args []string
	}{
		{"wl-copy", nil},
		{"xclip", []string{"-selection", "clipboard"}},
		{"xsel", []string{"--clipboard", "--input"}},
	}

	var lastErr error
	for _, c := range copiers {
		path, err := exec.LookPath(c.name)
		if err != nil {
			continue
		}
		cmd := exec.Command(path, c.args...)
		cmd.Stdin = strings.NewReader(text)
		if err := cmd.Run(); err != nil {
			lastErr = fmt.Errorf("%s: %w", c.name, err)
			continue
		}
		return nil
	}

	if osc52Err == nil {
		return nil
	}

	if lastErr != nil {
		return lastErr
	}

	return fmt.Errorf("no clipboard tool found (install wl-copy, xclip, or xsel)")
}
