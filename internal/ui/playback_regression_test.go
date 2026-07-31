package ui

// Regression tests for the playback auto-advance state machine and related
// playback bugs (scout report "youtui-bugs", 2026-07-31):
//
//   - Bug 1 (critical): playlist auto-advance silently died after any manual
//     skip because a shared `skipAutoPlay` flag was consumed by the wrong
//     wait goroutine. The flag was deleted; the process-identity guard alone
//     prevents double-advance. Tests: TestAutoAdvanceAfterManualSkip,
//     TestAutoAdvanceShuffleAfterManualSkip, TestAutoAdvanceRapidDoubleNext.
//   - Bug 2 (high): "Space — Play playlist from start" was documented in the
//     help screen but had no handler. Tests: TestSpacePlaysPlaylistFromStart,
//     TestSpaceOnEmptyPlaylistDoesNotPlay, TestSpaceOnPlayerBoxTogglesPause.
//   - Bug 4d: a corrupt/edited state file could restore an out-of-range
//     currentTrack. Test: TestRestoreStateClampsCurrentTrack.
//   - Bug 3: playlist modes were never persisted on change. Test:
//     TestModeChangesPersistToState.
//
// The harness mirrors the scout's: a real SimpleApp with a real tview event
// loop on a tcell.NewSimulationScreen, and a fake `mpv` shim on PATH that
// sleeps ~1s then exits 0, so "track finished" is observed exactly like a real
// natural end.

import (
	"fmt"
	"os"
	"path/filepath"
	"testing"
	"time"

	"github.com/IvelOt/youtui-player/internal/config"
	"github.com/gdamore/tcell/v2"
)

// fakeMpvScript simulates a track that finishes naturally after
// YOUTUI_FAKE_MPV_SLEEP seconds (default 1). A fail:// URL exits 1 so the
// mpv-error path can be exercised if needed.
const fakeMpvScript = `#!/bin/sh
sleep_s="${YOUTUI_FAKE_MPV_SLEEP:-1}"
for arg in "$@"; do
  case "$arg" in
    fail://*) exit 1 ;;
  esac
done
sleep "$sleep_s"
exit 0
`

// startAppLoop wires a simulation screen onto the app and runs the tview
// event loop (QueueUpdateDraw blocks until the loop drains it, so playback
// code needs the loop running to make progress). Cleanup kills any live mpv
// process, waits for the progress updater to fully exit, then terminates the
// event loop via stopAppLoop: a leftover loop would keep drawing — reading
// the global tview.Styles — while the next test's NewSimpleApp mutates those
// same globals.
func startAppLoop(t *testing.T, a *SimpleApp) {
	t.Helper()
	sim := tcell.NewSimulationScreen("UTF-8")
	a.app.SetScreen(sim) // calls sim.Init()
	sim.SetSize(120, 40)
	go a.app.Run()
	t.Cleanup(func() {
		a.cleanup() // kills any live (fake) mpv process, stops the updater

		// Wait for the progress-updater goroutine to exit (its final
		// QueueUpdateDraw, if any, happens-before close(stopProgressDone)),
		// so no further update can be queued once the barrier below proves
		// the loop drained everything up to that point. cleanup() itself
		// must not wait here: it may run on the event-loop goroutine in
		// production, and a wait could deadlock on the updater's update.
		a.mu.Lock()
		updaterDone := a.stopProgressDone
		a.mu.Unlock()
		if updaterDone != nil {
			<-updaterDone
		}

		stopAppLoop(t, a)
	})
}

// stopAppLoop ends the tview event loop with a real happens-before edge.
//
// The race hazard: the loop goroutine draws the UI (reading the global
// tview.Styles) while the next test's NewSimpleApp writes those globals. A
// wall-clock "wait a bit" heuristic would not satisfy the race detector, and
// tview's events channel is buffered, so QueueEvent(nil) alone returns before
// the loop has actually consumed the terminating event.
//
// Instead we use a barrier update: a.queueUpdate completes only after the
// loop has executed it, and (channel FIFO + single-threaded loop) every
// update queued before it — hence every draw the loop performed — happens
// before it. That chains: loop reads -> barrier done -> cleanup return ->
// next test's NewSimpleApp. By the time the barrier runs, the mpv process is
// dead (its wait goroutine returns at the identity check without queueing)
// and the progress updater has fully exited (startAppLoop's cleanup waited
// on stopProgressDone), so nothing can queue a further update; the loop's
// next select has only the terminating event ready and breaks immediately.
func stopAppLoop(t *testing.T, a *SimpleApp) {
	t.Helper()

	// Barrier: completes only after every previously queued update ran.
	done := make(chan struct{})
	go func() {
		a.app.QueueUpdate(func() { close(done) })
	}()
	select {
	case <-done:
	case <-time.After(5 * time.Second):
		t.Errorf("stopAppLoop(%s): barrier update never executed; loop stalled", t.Name())
		return
	}

	a.app.QueueEvent(nil) // tview's "stop the loop" signal
}

// newTestApp builds a fully wired SimpleApp with an isolated environment:
// XDG dirs point at temp dirs, a fake mpv shim is first on PATH, and the
// playlist is populated with playlistLen fake tracks.
func newTestApp(t *testing.T, playlistLen int) *SimpleApp {
	t.Helper()

	t.Setenv("XDG_CONFIG_HOME", t.TempDir())
	t.Setenv("XDG_STATE_HOME", t.TempDir())
	t.Setenv("XDG_CACHE_HOME", t.TempDir())
	t.Setenv("XDG_DATA_HOME", t.TempDir())

	binDir := t.TempDir()
	mpvShim := filepath.Join(binDir, "mpv")
	if err := os.WriteFile(mpvShim, []byte(fakeMpvScript), 0o755); err != nil {
		t.Fatal(err)
	}
	t.Setenv("PATH", binDir+string(os.PathListSeparator)+os.Getenv("PATH"))

	a := NewSimpleApp("test")
	startAppLoop(t, a)

	a.mu.Lock()
	for i := 0; i < playlistLen; i++ {
		a.playlistTracks = append(a.playlistTracks, Track{
			Title:    fmt.Sprintf("Track %d", i+1),
			Author:   "Test Artist",
			URL:      fmt.Sprintf("https://example.invalid/%d", i),
			Duration: "1:00",
		})
	}
	tracks := make([]Track, len(a.playlistTracks))
	copy(tracks, a.playlistTracks)
	a.mu.Unlock()

	// UI primitives must only be touched from the event-loop goroutine, so
	// populate the playlist widget through a queued update.
	a.app.QueueUpdateDraw(func() {
		for i, tr := range tracks {
			a.playlist.AddItem(tr, i)
		}
	})

	return a
}

// appState returns a snapshot of the playback state under the app mutex.
func appState(a *SimpleApp) (isPlaying bool, currentTrack int) {
	a.mu.Lock()
	defer a.mu.Unlock()
	return a.isPlaying, a.currentTrack
}

// waitFor polls cond until it returns true or the timeout elapses.
func waitFor(t *testing.T, timeout time.Duration, desc string, cond func() bool) {
	t.Helper()
	deadline := time.Now().Add(timeout)
	for time.Now().Before(deadline) {
		if cond() {
			return
		}
		time.Sleep(50 * time.Millisecond)
	}
	t.Fatalf("timeout waiting for %s", desc)
}

// waitForPlaying waits until isPlaying is true with the given currentTrack.
func waitForPlaying(t *testing.T, a *SimpleApp, idx int) {
	t.Helper()
	waitFor(t, 20*time.Second, fmt.Sprintf("track %d playing", idx), func() bool {
		playing, cur := appState(a)
		return playing && cur == idx
	})
}

// TestAutoAdvanceNaturalEnd is the baseline (scout Scenario 1): with no manual
// interaction, tracks advance A -> B -> C.
func TestAutoAdvanceNaturalEnd(t *testing.T) {
	a := newTestApp(t, 5)

	a.playTrackSimple(a.playlistTracks[0], 0)
	waitForPlaying(t, a, 0)
	waitForPlaying(t, a, 1)
	waitForPlaying(t, a, 2)
}

// TestAutoAdvanceAfterManualSkip is the headline regression (scout Scenario 2):
// play A, manually skip to B ('n'), B ends naturally -> C must start. Before
// the fix, the skipAutoPlay flag was consumed by B's wait goroutine, which
// swallowed the auto-advance and froze the playlist on B.
func TestAutoAdvanceAfterManualSkip(t *testing.T) {
	a := newTestApp(t, 5)

	a.playTrackSimple(a.playlistTracks[0], 0)
	waitForPlaying(t, a, 0)

	a.playNext() // manual skip, like pressing 'n'

	waitForPlaying(t, a, 1)

	// The regression: B's natural end must still auto-advance to C.
	waitForPlaying(t, a, 2)
}

// TestAutoAdvanceShuffleAfterManualSkip is scout Scenario 4: in shuffle mode a
// manual skip used to permanently kill the random auto-advance ("shuffle only
// plays one random song and stops").
func TestAutoAdvanceShuffleAfterManualSkip(t *testing.T) {
	a := newTestApp(t, 5)

	a.mu.Lock()
	a.playlistMode = ModeShuffle
	a.mu.Unlock()

	a.playTrackSimple(a.playlistTracks[0], 0)
	waitForPlaying(t, a, 0)

	a.playNext() // manual skip

	waitFor(t, 20*time.Second, "manual skip to a different track", func() bool {
		playing, cur := appState(a)
		return playing && cur != 0
	})
	_, skipped := appState(a)

	// The skipped-to track ends naturally: shuffle must advance again.
	waitFor(t, 20*time.Second, "shuffle auto-advance after natural end", func() bool {
		playing, cur := appState(a)
		return playing && cur != skipped
	})
}

// TestAutoAdvanceRapidDoubleNext is scout Scenario 10: two rapid 'n' presses.
// The second skip replaces the first skipped-to track's process; its wait
// goroutine must exit at the identity check, and the final track's natural end
// must still advance.
func TestAutoAdvanceRapidDoubleNext(t *testing.T) {
	a := newTestApp(t, 5)

	a.playTrackSimple(a.playlistTracks[0], 0)
	waitForPlaying(t, a, 0)

	a.playNext()
	waitForPlaying(t, a, 1)

	time.Sleep(150 * time.Millisecond)
	a.playNext()
	waitForPlaying(t, a, 2)

	// C ends naturally -> must advance to D (index 3).
	waitForPlaying(t, a, 3)
}

// TestSpacePlaysPlaylistFromStart covers Bug 2: Space with the playlist
// focused starts playback from the first track (help screen documents
// "Space — Play playlist from start"). It must work even when nothing is
// playing (e.g. after a restart where n/p answer "NothingPlaying").
func TestSpacePlaysPlaylistFromStart(t *testing.T) {
	a := newTestApp(t, 3)

	space := tcell.NewEventKey(tcell.KeyRune, ' ', tcell.ModNone)
	if ret := a.handleKeyPress(space, a.playlist.Flex); ret != nil {
		t.Fatalf("Space on focused playlist should be consumed by the handler, got %v", ret)
	}

	waitForPlaying(t, a, 0)
}

// TestSpaceOnEmptyPlaylistDoesNotPlay ensures the empty-playlist guard.
func TestSpaceOnEmptyPlaylistDoesNotPlay(t *testing.T) {
	a := newTestApp(t, 0)

	space := tcell.NewEventKey(tcell.KeyRune, ' ', tcell.ModNone)
	if ret := a.handleKeyPress(space, a.playlist.Flex); ret != nil {
		t.Fatalf("Space on focused playlist should be consumed by the handler, got %v", ret)
	}

	time.Sleep(300 * time.Millisecond)
	playing, _ := appState(a)
	if playing {
		t.Fatal("Space must not start playback with an empty playlist")
	}
}

// TestSpaceOnPlayerBoxTogglesPause keeps the legacy Space-on-player behavior
// (pause) intact after the handler split.
func TestSpaceOnPlayerBoxTogglesPause(t *testing.T) {
	a := newTestApp(t, 3)

	a.playTrackSimple(a.playlistTracks[0], 0)
	waitForPlaying(t, a, 0)

	space := tcell.NewEventKey(tcell.KeyRune, ' ', tcell.ModNone)
	if ret := a.handleKeyPress(space, a.playerBox); ret != nil {
		t.Fatalf("Space on focused player box should be consumed by the handler, got %v", ret)
	}
}

// TestRestoreStateClampsCurrentTrack covers Bug 4d: a corrupt/edited state
// file with an out-of-range current_track_idx used to be restored verbatim and
// could panic playPrevious (unguarded playlistTracks[prev]). It must now be
// clamped to -1 ("not in playlist").
func TestRestoreStateClampsCurrentTrack(t *testing.T) {
	t.Setenv("XDG_CONFIG_HOME", t.TempDir())
	t.Setenv("XDG_STATE_HOME", t.TempDir())

	state := &config.PlayerState{
		CurrentTrackIdx: 99, // out of range: playlist only has 2 tracks
		Playlist: []config.Track{
			{Title: "A", URL: "https://example.invalid/a"},
			{Title: "B", URL: "https://example.invalid/b"},
		},
	}
	if err := config.SaveState(state); err != nil {
		t.Fatal(err)
	}

	a := NewSimpleApp("test")
	startAppLoop(t, a)

	// NewSimpleApp restores state in a background goroutine.
	waitFor(t, 10*time.Second, "currentTrack clamped to -1", func() bool {
		_, cur := appState(a)
		return cur == -1
	})

	// The previously panicking paths must be safe with the clamped state.
	a.playNext()
	a.playPrevious()
}

// TestRestoreStateKeepsValidCurrentTrack ensures an in-range restored index is
// preserved (the clamp must not wipe legitimate state).
func TestRestoreStateKeepsValidCurrentTrack(t *testing.T) {
	t.Setenv("XDG_CONFIG_HOME", t.TempDir())
	t.Setenv("XDG_STATE_HOME", t.TempDir())

	state := &config.PlayerState{
		CurrentTrackIdx: 1,
		Playlist: []config.Track{
			{Title: "A", URL: "https://example.invalid/a"},
			{Title: "B", URL: "https://example.invalid/b"},
		},
	}
	if err := config.SaveState(state); err != nil {
		t.Fatal(err)
	}

	a := NewSimpleApp("test")
	startAppLoop(t, a)

	waitFor(t, 10*time.Second, "valid currentTrack preserved", func() bool {
		_, cur := appState(a)
		return cur == 1
	})
}

// TestModeChangesPersistToState covers Bug 3: toggling shuffle/repeat used to
// discard the mode on restart because neither toggle saved state. It also
// verifies the shuffle -> normal guard in cycleRepeatMode (previously a silent
// no-op).
func TestModeChangesPersistToState(t *testing.T) {
	a := newTestApp(t, 0)

	waitForStateMode := func(want PlaylistMode) {
		t.Helper()
		waitFor(t, 10*time.Second, fmt.Sprintf("state playlist_mode == %s", want), func() bool {
			st, err := config.LoadState()
			return err == nil && st != nil && st.PlaylistMode == int(want)
		})
	}

	a.cycleRepeatMode() // Normal -> RepeatOne
	waitForStateMode(ModeRepeatOne)

	a.cycleRepeatMode() // RepeatOne -> RepeatAll
	waitForStateMode(ModeRepeatAll)

	a.toggleShuffle() // RepeatAll -> Shuffle
	waitForStateMode(ModeShuffle)

	a.cycleRepeatMode() // Shuffle -> Normal (was a silent no-op)
	waitForStateMode(ModeNormal)
}
