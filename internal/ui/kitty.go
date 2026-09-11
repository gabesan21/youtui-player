package ui

import (
	"encoding/base64"
	"fmt"
	"io"
	"os"
	"slices"
	"strings"
	"time"

	"golang.org/x/sys/unix"
)

// Kitty graphics protocol subset, hand-rolled per the recon decisions:
// transmit image files from the on-disk cache without displaying them
// (a=t, t=f — always the derived PNG, never the JPEG), place a source pixel
// crop by cell size at the cursor position (a=p with x/y/w/h + c/r), and
// delete by placement id (a=d, d=p). No Unicode placeholders, so there is no
// tmux passthrough.
//
// All KittyRenderer methods and emitters MUST be called from the tview main
// loop (SetAfterDrawFunc / SetBeforeDrawFunc / QueueUpdateDraw callbacks) or
// after Application.Run() returns. Emissions write raw APC escapes to stdout,
// interleaved with tcell output; confining them to the main loop (and to
// afterDraw, which tview runs before screen.Show()) keeps the stream ordered
// w.r.t. tcell's flush. q=2 suppresses terminal responses so kitty never
// injects reply escapes that tcell would misread as input.

const (
	kittyAPCStart = "\x1b_G"
	kittyAPCEnd   = "\x1b\\"
	// kittyZIndexBelowText draws the image below text but above cell
	// backgrounds: the placeholder's blank cells keep the theme background
	// visible under the image and list text can overlap it if needed.
	kittyZIndexBelowText = -1
)

// kittyAvailable decides whether the Kitty sink may be used: the config must
// allow it ("blocks" forces the fallback), the terminal must be Kitty, and
// tmux disables it (no escape passthrough in this iteration).
func kittyAvailable(imageMode string) bool {
	switch imageMode {
	case "auto", "kitty":
	default:
		return false
	}
	if os.Getenv("TMUX") != "" {
		return false
	}
	return os.Getenv("TERM") == "xterm-kitty" || os.Getenv("KITTY_WINDOW_ID") != ""
}

// syncKittyPlacements runs from SetAfterDrawFunc — after tview's Draw (widget
// rects are current) and before tcell's flush (escapes stay ordered). It
// reconciles terminal placements with what the current layout wants: the
// player box plus the visible list rows. While a modal owns the screen the
// thumbnail areas are not drawn, so all placements are invalidated instead of
// re-placed at stale coordinates.
func (a *SimpleApp) syncKittyPlacements() {
	if a.kitty == nil {
		return
	}
	if a.inModal {
		a.kitty.Invalidate(os.Stdout)
		return
	}

	desired := make(map[string]kittySinkSpec)
	if a.kittyPlayerPath != "" && a.playerKittyBox != nil && a.playerBox != nil {
		// Clamp to the player box interior: kitty placements ignore tview's
		// cell clipping and would otherwise paint over neighboring panels.
		x, y, w, h := a.playerKittyBox.GetInnerRect()
		cx, cy, cw, ch := a.playerBox.GetInnerRect()
		if spec, ok := newKittySinkSpec(a.kittyPlayerPath,
			kittyRect{x: x, y: y, w: w, h: h},
			a.kittyPlayerSrcW, a.kittyPlayerSrcH,
			a.kitty.cell, kittyRect{x: cx, y: cy, w: cw, h: ch}); ok {
			desired["player"] = spec
		}
	}
	for key, spec := range a.searchResults.kittySinkSpecs("search", a.kitty.cell) {
		desired[key] = spec
	}
	for key, spec := range a.playlist.kittySinkSpecs("playlist", a.kitty.cell) {
		desired[key] = spec
	}

	generations := map[string]uint64{
		"search":   a.searchResults.KittyRenderGeneration(),
		"playlist": a.playlist.KittyRenderGeneration(),
	}
	a.kitty.Sync(desired, generations, os.Stdout)
}

type kittyRect struct {
	x, y, w, h int
}

// intersect returns the overlap of two rects, or the zero rect when disjoint.
func (r kittyRect) intersect(o kittyRect) kittyRect {
	x0 := max(r.x, o.x)
	y0 := max(r.y, o.y)
	x1 := min(r.x+r.w, o.x+o.w)
	y1 := min(r.y+r.h, o.y+o.h)
	if x1 <= x0 || y1 <= y0 {
		return kittyRect{}
	}
	return kittyRect{x: x0, y: y0, w: x1 - x0, h: y1 - y0}
}

// kittySinkSpec is the desired state of one placement slot (a list row or the
// player box) for the current frame: the (clamped) target cell rect and the
// source pixel crop to display in it.
type kittySinkSpec struct {
	path string
	rect kittyRect
	src  kittyRect
}

// kittyCellSize is the terminal cell geometry in pixels; only the w:h ratio
// feeds the aspect-correct source crop (the clamp remap works in cell units).
type kittyCellSize struct {
	w, h int
}

// measureKittyCellSize reads TIOCGWINSZ on stdout. When the ioctl fails or
// the terminal reports no pixel geometry, it falls back to the common 1:2
// cell aspect (w:h).
func measureKittyCellSize() kittyCellSize {
	ws, err := unix.IoctlGetWinsize(int(os.Stdout.Fd()), unix.TIOCGWINSZ)
	if err == nil && ws.Xpixel > 0 && ws.Ypixel > 0 && ws.Col > 0 && ws.Row > 0 {
		return kittyCellSize{w: int(ws.Xpixel / ws.Col), h: int(ws.Ypixel / ws.Row)}
	}
	return kittyCellSize{w: 1, h: 2}
}

// newKittySinkSpec builds the placement for one sink. The source image is
// center-cropped to the exact aspect of the target pixel rect (no stretch);
// the target is then clamped to the visible canvas of its owning panel, and
// the clamped rect is mapped back into the source crop proportionally, so a
// partially visible row shows the matching partial image — exactly what
// tcell's cell clipping does for the blocks sink. ok=false means the sink is
// fully clipped (or not laid out yet) and contributes nothing this frame, so
// Sync deletes any stale placement.
func newKittySinkSpec(path string, target kittyRect, srcW, srcH int, cell kittyCellSize, clip kittyRect) (kittySinkSpec, bool) {
	if target.w <= 0 || target.h <= 0 || srcW <= 0 || srcH <= 0 {
		return kittySinkSpec{}, false
	}

	// Center-crop the source to the aspect of the target pixel rect,
	// comparing aspects in integer cross-products (no floats).
	targetW := target.w * cell.w
	targetH := target.h * cell.h
	crop := kittyRect{w: srcW, h: srcH}
	if srcW*targetH > srcH*targetW {
		// Source wider than the target: crop the sides.
		crop.w = srcH * targetW / targetH
		crop.x = (srcW - crop.w) / 2
	} else {
		// Source taller than the target: crop top and bottom.
		crop.h = srcW * targetH / targetW
		crop.y = (srcH - crop.h) / 2
	}

	visible := target.intersect(clip)
	if visible.w <= 0 || visible.h <= 0 {
		return kittySinkSpec{}, false
	}

	if visible != target {
		// Offsets scale with the crop extent before it shrinks — the cell
		// pixel size cancels out of the proportional mapping.
		crop.x += (visible.x - target.x) * crop.w / target.w
		crop.y += (visible.y - target.y) * crop.h / target.h
		crop.w = max(visible.w*crop.w/target.w, 1)
		crop.h = max(visible.h*crop.h/target.h, 1)
	}

	return kittySinkSpec{path: path, rect: visible, src: crop}, true
}

type kittySink struct {
	spec        kittySinkSpec
	imageID     uint32
	placementID uint32
	placed      bool
}

// KittyRenderer owns the terminal-side image placements and reconciles them
// against the desired per-frame state. Main-loop only: no locking, by design.
type KittyRenderer struct {
	sinks       map[string]*kittySink
	transmitted map[string]uint32 // cache file path -> transmitted image id
	generations map[string]uint64 // list prefix -> last seen render generation
	cell        kittyCellSize
	nextImageID uint32
	nextPlaceID uint32
	anyPlaced   bool
	// debugPath comes from YOUTUI_KITTY_DEBUG; debugBuf accumulates one
	// Sync's decisions and is flushed to that file at the end of the Sync.
	// Both are nil/empty when the env var is unset — a silent no-op.
	debugPath string
	debugBuf  *strings.Builder
}

func NewKittyRenderer() *KittyRenderer {
	r := &KittyRenderer{
		sinks:       make(map[string]*kittySink),
		transmitted: make(map[string]uint32),
		generations: make(map[string]uint64),
		debugPath:   os.Getenv("YOUTUI_KITTY_DEBUG"),
	}
	r.RefreshCellSize()
	return r
}

// RefreshCellSize re-measures the terminal cell geometry; call it on resize,
// before Invalidate, so re-placed crops use the new cell pixel ratio.
func (r *KittyRenderer) RefreshCellSize() {
	r.cell = measureKittyCellSize()
}

// Sync diffs the desired placements against the live ones: gone sinks are
// deleted, and every changed sink is deleted-then-re-placed with fresh ids
// (see placeSink) — there is no in-place re-place with the same ids.
// A generation bump of a sink's list (the key prefix) forces the re-place
// even when the spec coincidentally compares equal, because the widget rects
// behind an equal spec may still have moved (scroll in any direction).
// Unchanged, unforced placements are not re-emitted — kitty placements
// persist across tcell repaints, so re-sending them every frame would only
// add traffic.
func (r *KittyRenderer) Sync(desired map[string]kittySinkSpec, generations map[string]uint64, w io.Writer) {
	r.beginDebug(desired)

	for key, sink := range r.sinks {
		spec, wanted := desired[key]
		if !wanted {
			r.debugf("delete key=%s i=%d p=%d\n", key, sink.imageID, sink.placementID)
			r.deleteSink(sink, w)
			delete(r.sinks, key)
			continue
		}
		r.placeSink(key, sink, spec, r.generationBumped(key, generations), w)
	}
	for key, spec := range desired {
		if _, ok := r.sinks[key]; ok {
			continue
		}
		sink := &kittySink{}
		r.sinks[key] = sink
		r.generationBumped(key, generations)
		r.placeSink(key, sink, spec, false, w)
	}

	r.anyPlaced = false
	for _, sink := range r.sinks {
		if sink.placed {
			r.anyPlaced = true
			break
		}
	}

	r.flushDebug()
}

// generationBumped records the list's current render generation and reports
// whether it changed since the last Sync. The prefix of a sink key ("search",
// "playlist") selects the list; the "player" key has no generation entry and
// never forces.
func (r *KittyRenderer) generationBumped(key string, generations map[string]uint64) bool {
	prefix := key
	if i := strings.IndexByte(key, ':'); i >= 0 {
		prefix = key[:i]
	}
	gen := generations[prefix]
	bumped := gen != r.generations[prefix]
	r.generations[prefix] = gen
	return bumped
}

// placeSink converges one sink to the desired spec, emitting nothing only
// when the live placement already matches it and no re-place is forced. Any
// other case deletes the old placement first and places with a fresh
// placement id — plus a fresh transmit (new image id) when the image path
// changed — so the terminal can never keep a stale frame paired with the
// current spec.
func (r *KittyRenderer) placeSink(key string, sink *kittySink, spec kittySinkSpec, force bool, w io.Writer) {
	if !force && sink.placed && sink.spec == spec {
		return
	}
	pathChanged := !sink.placed || sink.spec.path != spec.path
	if sink.placed {
		r.debugf("delete key=%s i=%d p=%d (replace)\n", key, sink.imageID, sink.placementID)
		r.deleteSink(sink, w)
	}
	if pathChanged {
		sink.imageID = r.transmit(w, spec.path)
	}
	sink.spec = spec
	sink.placementID = r.nextPlacementID()
	sink.placed = true
	r.debugf("place key=%s i=%d p=%d rect=%d,%d %dx%d src=%d,%d %dx%d force=%v fresh-image=%v\n",
		key, sink.imageID, sink.placementID,
		spec.rect.x, spec.rect.y, spec.rect.w, spec.rect.h,
		spec.src.x, spec.src.y, spec.src.w, spec.src.h,
		force, pathChanged)
	kittyPlace(w, sink.imageID, sink.placementID, spec)
}

// beginDebug starts the per-Sync debug record when YOUTUI_KITTY_DEBUG names
// a file; flushDebug appends it at the end of the Sync. One open/append/close
// per Sync keeps it main-loop-cheap, and unset env means literally no I/O.
func (r *KittyRenderer) beginDebug(desired map[string]kittySinkSpec) {
	if r.debugPath == "" {
		return
	}
	r.debugBuf = &strings.Builder{}
	fmt.Fprintf(r.debugBuf, "[%s] desired=%v live=%v\n",
		time.Now().Format(time.RFC3339Nano),
		sortedKeys(desired), sortedKeys(r.sinks))
}

func (r *KittyRenderer) debugf(format string, args ...any) {
	if r.debugBuf == nil {
		return
	}
	fmt.Fprintf(r.debugBuf, format, args...)
}

func (r *KittyRenderer) flushDebug() {
	if r.debugBuf == nil {
		return
	}
	defer func() { r.debugBuf = nil }()
	f, err := os.OpenFile(r.debugPath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0o644)
	if err != nil {
		return
	}
	defer func() { _ = f.Close() }()
	_, _ = io.WriteString(f, r.debugBuf.String())
}

func sortedKeys[V any](m map[string]V) []string {
	keys := make([]string, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	slices.Sort(keys)
	return keys
}

// Invalidate deletes every placement and forgets the transmitted registry, so
// the next Sync re-transmits and re-places from scratch. Used on resize and
// whenever the thumbnail areas leave the visible layout (modals). The registry
// reset is deliberate hardening: real terminals may free image data when
// placements are deleted, so re-placing without re-transmitting is unsafe.
func (r *KittyRenderer) Invalidate(w io.Writer) {
	if !r.anyPlaced {
		return
	}
	kittyDeleteAllPlacements(w)
	for _, sink := range r.sinks {
		sink.placed = false
	}
	r.transmitted = make(map[string]uint32)
	r.anyPlaced = false
}

// DeleteAll removes all placements and image data from the terminal. Call it
// on exit so no image outlives the app.
func (r *KittyRenderer) DeleteAll(w io.Writer) {
	kittyDeleteEverything(w)
	r.sinks = make(map[string]*kittySink)
	r.transmitted = make(map[string]uint32)
	r.anyPlaced = false
}

func (r *KittyRenderer) deleteSink(sink *kittySink, w io.Writer) {
	if !sink.placed {
		return
	}
	kittyDeletePlacement(w, sink.imageID, sink.placementID)
	sink.placed = false
}

func (r *KittyRenderer) transmit(w io.Writer, path string) uint32 {
	if id, ok := r.transmitted[path]; ok {
		return id
	}
	r.nextImageID++
	r.transmitted[path] = r.nextImageID
	kittyTransmitFile(w, r.nextImageID, path)
	return r.nextImageID
}

func (r *KittyRenderer) nextPlacementID() uint32 {
	r.nextPlaceID++
	return r.nextPlaceID
}

// kittyTransmitFile transmits the image from a local path without displaying
// it (a=t, t=f; a=T would also display at the cursor). f=100 makes the
// terminal read a container format from the file — the sink always passes the
// derived PNG, since the protocol accepts only RGB/RGBA/PNG payloads. Cache
// paths are short enough to fit a single unchunked payload.
func kittyTransmitFile(w io.Writer, id uint32, path string) {
	payload := base64.StdEncoding.EncodeToString([]byte(path))
	fmt.Fprintf(w, "%sa=t,t=f,f=100,i=%d,q=2;%s%s", kittyAPCStart, id, payload, kittyAPCEnd)
}

// kittyPlace anchors the placement at the cursor, so it first emits a CUP
// (1-based) to the target cell; C=1 keeps the cursor unmoved for tcell, which
// repositions it during the flush that follows afterDraw anyway. The source
// keys x/y/w/h select the pixel region of the transmitted image that is
// scaled into the c×r target cells.
func kittyPlace(w io.Writer, imageID, placementID uint32, spec kittySinkSpec) {
	fmt.Fprintf(w, "\x1b[%d;%dH", spec.rect.y+1, spec.rect.x+1)
	fmt.Fprintf(w, "%sa=p,i=%d,p=%d,x=%d,y=%d,w=%d,h=%d,c=%d,r=%d,z=%d,C=1,q=2;%s",
		kittyAPCStart, imageID, placementID,
		spec.src.x, spec.src.y, spec.src.w, spec.src.h,
		spec.rect.w, spec.rect.h, kittyZIndexBelowText, kittyAPCEnd)
}

func kittyDeletePlacement(w io.Writer, imageID, placementID uint32) {
	fmt.Fprintf(w, "%sa=d,d=p,i=%d,p=%d,q=2;%s", kittyAPCStart, imageID, placementID, kittyAPCEnd)
}

// Lowercase d=a deletes placements but keeps image data; uppercase d=A frees
// the transmitted images too (exit path).
func kittyDeleteAllPlacements(w io.Writer) {
	fmt.Fprintf(w, "%sa=d,d=a,q=2;%s", kittyAPCStart, kittyAPCEnd)
}

func kittyDeleteEverything(w io.Writer) {
	fmt.Fprintf(w, "%sa=d,d=A,q=2;%s", kittyAPCStart, kittyAPCEnd)
}
