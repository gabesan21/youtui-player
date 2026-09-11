package ui

func (a *SimpleApp) updateThumbnail(thumbnailURL string) {
	if a.kitty != nil {
		a.kittyPlayerPath = ""
		if thumbnailURL == "" || a.thumbCache == nil {
			return
		}

		go func() {
			path, w, h, err := a.thumbCache.GetThumbnailPNG(thumbnailURL)
			if err != nil {
				return
			}

			a.app.QueueUpdateDraw(func() {
				if a.thumbnailFetchStale(thumbnailURL) {
					return
				}
				a.kittyPlayerPath = path
				a.kittyPlayerSrcW = w
				a.kittyPlayerSrcH = h
			})
		}()
		return
	}

	if thumbnailURL == "" || a.thumbCache == nil {
		a.thumbnailView.SetImage(nil)
		return
	}

	go func() {
		img, err := a.thumbCache.GetThumbnailImage(thumbnailURL)
		if err != nil {
			return
		}

		a.app.QueueUpdateDraw(func() {
			if a.thumbnailFetchStale(thumbnailURL) {
				return
			}
			a.thumbnailView.SetImage(img)
		})
	}()
}

// thumbnailFetchStale drops fetches overtaken by playback state: a new track
// replaced the URL, or playback stopped (updateThumbnail("") clears the view
// synchronously, but an in-flight fetch from the old track must not repaint).
func (a *SimpleApp) thumbnailFetchStale(thumbnailURL string) bool {
	a.mu.Lock()
	defer a.mu.Unlock()
	return !a.isPlaying || a.currentThumb != thumbnailURL
}
