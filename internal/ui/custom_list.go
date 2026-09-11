package ui

import (
	"fmt"
	"image"
	"sync"

	"github.com/gdamore/tcell/v2"
	"github.com/rivo/tview"
)

type CustomListItem struct {
	flex      *tview.Flex
	thumbnail *tview.Image // blocks sink; nil in kitty mode
	kittyBox  *tview.Box   // blank placeholder owning the cells; nil in blocks mode
	kittyPath string       // cache path once the kitty thumbnail is loaded
	kittySrcW int          // source pixel dimensions of the kitty image
	kittySrcH int
	info      *tview.TextView
	index     int
	track     Track
}

type CustomList struct {
	*tview.Flex
	container     *tview.Flex
	items         []*CustomListItem
	selectedIndex int
	playingIndex  int
	theme         *Theme
	kittyMode     bool
	mu            sync.Mutex
	onSelected    func(index int)
	visibleStart  int
	visibleHeight int
	lastHeight    int
	dirty         bool
}

func NewCustomList(theme *Theme, kittyMode bool) *CustomList {
	container := tview.NewFlex().SetDirection(tview.FlexRow)
	container.SetBackgroundColor(theme.Base)

	wrapper := tview.NewFlex().
		SetDirection(tview.FlexRow).
		AddItem(container, 0, 1, false)
	wrapper.SetBackgroundColor(theme.Mantle)

	list := &CustomList{
		Flex:          wrapper,
		container:     container,
		items:         []*CustomListItem{},
		selectedIndex: 0,
		playingIndex:  -1,
		theme:         theme,
		kittyMode:     kittyMode,
		visibleStart:  0,
		visibleHeight: 10,
	}

	wrapper.SetBorder(true).
		SetTitle(" ").
		SetBorderColor(theme.Surface1)

	wrapper.SetInputCapture(func(event *tcell.EventKey) *tcell.EventKey {
		switch event.Key() {
		case tcell.KeyUp:
			list.SelectPrevious()
			return nil
		case tcell.KeyDown:
			list.SelectNext()
			return nil
		case tcell.KeyEnter:
			if list.onSelected != nil {
				list.onSelected(list.selectedIndex)
			}
			return nil
		case tcell.KeyTab, tcell.KeyBacktab:
			return event
		}
		return event
	})

	list.renderVisibleItems()
	return list
}

func (c *CustomList) AddItem(track Track, index int) {
	c.mu.Lock()
	defer c.mu.Unlock()

	item := &CustomListItem{
		info: tview.NewTextView().
			SetDynamicColors(true).
			SetText(formatItemInfo(track, index, c.theme)).
			SetTextAlign(tview.AlignLeft),
		index: index,
		track: track,
	}
	item.info.SetBackgroundColor(c.theme.Base)
	item.info.SetTextColor(c.theme.Text)

	var thumbPrimitive tview.Primitive
	if c.kittyMode {
		// Blank placeholder: the Kitty image lives in a separate terminal
		// layer, so tcell keeps owning these cells (theme background only).
		item.kittyBox = tview.NewBox().SetBackgroundColor(c.theme.Base)
		thumbPrimitive = item.kittyBox
	} else {
		item.thumbnail = tview.NewImage().
			SetColors(tview.TrueColor).
			SetDithering(tview.DitheringFloydSteinberg)
		item.thumbnail.SetBackgroundColor(c.theme.Base)
		thumbPrimitive = item.thumbnail
	}

	itemFlex := tview.NewFlex().
		SetDirection(tview.FlexColumn).
		AddItem(thumbPrimitive, 20, 0, false).
		AddItem(item.info, 0, 1, false)
	itemFlex.SetBackgroundColor(c.theme.Base)
	// One empty row on top: breathing room between cards; the flex
	// background fills it, so selection/playing colors stay continuous.
	itemFlex.SetBorderPadding(1, 0, 0, 0)
	item.flex = itemFlex

	c.items = append(c.items, item)
	c.renderVisibleItems()
}

// SetThumbnail paints the blocks sink. The URL must still match the item's
// track: a fetch spawned before a page change or list rebuild must not paint
// over the item that now occupies the index.
func (c *CustomList) SetThumbnail(index int, url string, img image.Image) {
	c.mu.Lock()
	defer c.mu.Unlock()
	if index >= 0 && index < len(c.items) &&
		c.items[index].thumbnail != nil && c.items[index].track.Thumbnail == url {
		c.items[index].thumbnail.SetImage(img)
	}
}

// SetKittyThumbnail records the cache path and source pixel dimensions
// backing the item's Kitty placement, with the same stale-URL guard as
// SetThumbnail. The placement itself is emitted by
// SimpleApp.syncKittyPlacements on the next draw.
func (c *CustomList) SetKittyThumbnail(index int, url string, path string, srcW, srcH int) {
	c.mu.Lock()
	defer c.mu.Unlock()
	if index >= 0 && index < len(c.items) &&
		c.items[index].kittyBox != nil && c.items[index].track.Thumbnail == url {
		c.items[index].kittyPath = path
		c.items[index].kittySrcW = srcW
		c.items[index].kittySrcH = srcH
	}
}

// kittySinkSpecs returns the desired Kitty placements for the items in the
// visible window, keyed by prefix+index. Only the visible window contributes:
// items scrolled out of view keep stale rects and must not be re-placed.
// Every target rect is clamped to the container's inner rect — kitty
// placements ignore tview's cell clipping, so rows partially visible at the
// panel edge would otherwise paint over neighboring panels.
func (c *CustomList) kittySinkSpecs(prefix string, cell kittyCellSize) map[string]kittySinkSpec {
	c.mu.Lock()
	defer c.mu.Unlock()

	cx, cy, cw, ch := c.container.GetInnerRect()
	clip := kittyRect{x: cx, y: cy, w: cw, h: ch}

	specs := make(map[string]kittySinkSpec)
	end := min(c.visibleStart+c.visibleHeight, len(c.items))
	for i := c.visibleStart; i < end; i++ {
		item := c.items[i]
		if item.kittyPath == "" {
			continue
		}
		x, y, w, h := item.kittyBox.GetInnerRect()
		spec, ok := newKittySinkSpec(item.kittyPath,
			kittyRect{x: x, y: y, w: w, h: h},
			item.kittySrcW, item.kittySrcH, cell, clip)
		if !ok {
			continue
		}
		specs[fmt.Sprintf("%s:%d", prefix, i)] = spec
	}
	return specs
}

func (c *CustomList) Clear() {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.container.Clear()
	c.items = []*CustomListItem{}
	c.selectedIndex = 0
	c.visibleStart = 0
}

func (c *CustomList) renderVisibleItems() {
	c.container.Clear()

	_, _, _, wrapperHeight := c.GetInnerRect()

	availableHeight := wrapperHeight
	if availableHeight <= 0 {
		availableHeight = 10
	}

	// 3 content rows + 1 padding row (SetPadding in AddItem).
	const itemHeight = 4

	itemsPerPage := availableHeight / itemHeight

	c.visibleHeight = max(itemsPerPage, 1)

	end := min(c.visibleStart+itemsPerPage, len(c.items))

	if len(c.items) == 0 || itemsPerPage == 0 {
		spacer := tview.NewBox().SetBackgroundColor(c.theme.Base)
		c.container.AddItem(spacer, 0, 1, false)
	} else {
		itemsRendered := 0
		for i := c.visibleStart; i < end; i++ {
			c.container.AddItem(c.items[i].flex, itemHeight, 0, false)
			itemsRendered++
		}

		remainingHeight := availableHeight - (itemsRendered * itemHeight)
		if remainingHeight > 0 {
			spacer := tview.NewBox().SetBackgroundColor(c.theme.Base)
			c.container.AddItem(spacer, remainingHeight, 0, false)
		}
	}

	c.updateSelection()
}

func (c *CustomList) scrollToSelection() {
	if c.selectedIndex >= c.visibleStart+c.visibleHeight {
		c.visibleStart = c.selectedIndex - c.visibleHeight + 1
		c.renderVisibleItems()
	}
	if c.selectedIndex < c.visibleStart {
		c.visibleStart = c.selectedIndex
		c.renderVisibleItems()
	}
}

func (c *CustomList) SelectNext() {
	c.mu.Lock()
	defer c.mu.Unlock()
	if c.selectedIndex < len(c.items)-1 {
		c.selectedIndex++
		c.scrollToSelection()
		c.updateSelection()
	}
}

func (c *CustomList) SelectPrevious() {
	c.mu.Lock()
	defer c.mu.Unlock()
	if c.selectedIndex > 0 {
		c.selectedIndex--
		c.scrollToSelection()
		c.updateSelection()
	}
}

func (c *CustomList) SelectFirst() {
	c.mu.Lock()
	defer c.mu.Unlock()
	if len(c.items) > 0 {
		c.selectedIndex = 0
		c.scrollToSelection()
		c.updateSelection()
	}
}

func (c *CustomList) SelectLast() {
	c.mu.Lock()
	defer c.mu.Unlock()
	if len(c.items) > 0 {
		c.selectedIndex = len(c.items) - 1
		c.scrollToSelection()
		c.updateSelection()
	}
}

func (c *CustomList) GetCurrentItem() int {
	c.mu.Lock()
	defer c.mu.Unlock()
	return c.selectedIndex
}

func (c *CustomList) SetCurrentIndex(idx int) {
	c.mu.Lock()
	defer c.mu.Unlock()
	if idx >= 0 && idx < len(c.items) {
		c.selectedIndex = idx
		c.scrollToSelection()
		c.updateSelection()
	}
}

func (c *CustomList) GetCurrentTrack() *Track {
	c.mu.Lock()
	defer c.mu.Unlock()
	if c.selectedIndex >= 0 && c.selectedIndex < len(c.items) {
		return &c.items[c.selectedIndex].track
	}
	return nil
}

func (c *CustomList) IsFocused(app *tview.Application) bool {
	focused := app.GetFocus()
	return focused == c.Flex
}

func (c *CustomList) SetSelectedFunc(handler func(int)) {
	c.onSelected = handler
}

func (c *CustomList) updateSelection() {
	for i, item := range c.items {
		switch i {
		case c.selectedIndex:
			item.flex.SetBackgroundColor(c.theme.Blue)
			item.info.SetTextColor(c.theme.Crust)
			item.info.SetBackgroundColor(c.theme.Blue)
			item.info.SetText(formatItemInfoPlain(item.track, item.index))
		case c.playingIndex:
			item.flex.SetBackgroundColor(c.theme.Green)
			item.info.SetTextColor(c.theme.Crust)
			item.info.SetBackgroundColor(c.theme.Green)
			item.info.SetText(formatItemInfoPlain(item.track, item.index))
		default:
			item.flex.SetBackgroundColor(c.theme.Base)
			item.info.SetTextColor(c.theme.Text)
			item.info.SetBackgroundColor(c.theme.Base)
			item.info.SetText(formatItemInfo(item.track, item.index, c.theme))
		}
	}
}

func (c *CustomList) SetTitle(title string) *CustomList {
	c.Flex.SetTitle(title)
	return c
}

func (c *CustomList) SetBorderColor(color tcell.Color) *CustomList {
	c.Flex.SetBorderColor(color)
	return c
}

func (c *CustomList) SetPlayingIndex(idx int) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.playingIndex = idx
	c.updateSelection()
}

func formatItemInfo(track Track, index int, theme *Theme) string {
	icons := []string{"♪", "♫", "♬"}
	icon := icons[index%len(icons)]
	title := track.Title
	if len(title) > 50 {
		title = title[:47] + "..."
	}
	return icon + " [" + colorTag(theme.Yellow) + "::b]" + title + "[-:-:-]\n" +
		"[" + colorTag(theme.Green) + "]⏱ " + track.Duration + "[-] " +
		"[" + colorTag(theme.Sapphire) + "]• " + track.Author + "[-]"
}

func formatItemInfoPlain(track Track, index int) string {
	icons := []string{"♪", "♫", "♬"}
	icon := icons[index%len(icons)]
	title := track.Title
	if len(title) > 50 {
		title = title[:47] + "..."
	}
	return icon + " " + title + "\n" +
		"⏱ " + track.Duration + " • " + track.Author
}

func (c *CustomList) MarkDirty() {
	c.dirty = true
}

func (c *CustomList) RefreshIfResized() {
	if !c.dirty {
		return
	}
	_, _, _, h := c.GetInnerRect()
	if h > 0 {
		c.dirty = false
		c.lastHeight = h
		c.renderVisibleItems()
	}
}

func (c *CustomList) SetTheme(theme *Theme) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.theme = theme
	c.SetBorderColor(theme.Surface1)
	c.SetBackgroundColor(theme.Mantle)
	c.container.SetBackgroundColor(theme.Base)
	for _, item := range c.items {
		item.flex.SetBackgroundColor(theme.Base)
		if item.thumbnail != nil {
			item.thumbnail.SetBackgroundColor(theme.Base)
		}
		if item.kittyBox != nil {
			item.kittyBox.SetBackgroundColor(theme.Base)
		}
		item.info.SetBackgroundColor(theme.Base)
		item.info.SetTextColor(theme.Text)
	}
	c.renderVisibleItems()
}
