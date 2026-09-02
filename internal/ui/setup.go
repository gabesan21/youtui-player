package ui

import (
	"fmt"
	"strings"

	"github.com/gabesan21/youtui-player/internal/config"
	"github.com/gabesan21/youtui-player/internal/search"
	"github.com/gdamore/tcell/v2"
	"github.com/rivo/tview"
)

func (a *SimpleApp) setupUI() {
	a.initLanguageFromConfig()

	a.setupSearchComponents()
	a.setupPlaylistComponent()
	a.setupDetailsComponent()
	a.setupPlayerComponents()
	a.setupStatusBars()
	a.setupHelpView()
	a.setupConfigView()
	a.setupLayout()
	a.setupInputHandlers()
	a.setupResizeHandler()
}

func (a *SimpleApp) setupSearchComponents() {
	a.searchInput = tview.NewInputField().
		SetLabel(" ").
		SetFieldBackgroundColor(a.theme.Surface0).
		SetFieldTextColor(a.theme.Text)

	a.searchInput.SetBorder(true).
		SetTitle(" " + a.strings.Search + " ").
		SetTitleAlign(tview.AlignLeft).
		SetBorderColor(a.theme.Blue)

	a.searchInput.SetDoneFunc(a.onSearchDone)

	a.searchResults = NewCustomList(a.theme)
	a.searchResults.SetTitle(" " + a.strings.Results + " [0] ")
	a.searchResults.SetSelectedFunc(func(idx int) {
		a.onResultSelectedCustom()
	})
}

func (a *SimpleApp) setupPlaylistComponent() {
	a.playlist = NewCustomList(a.theme)
	a.playlist.SetTitle(fmt.Sprintf(" %s [0] ", a.strings.Playlist))
	a.playlist.SetSelectedFunc(func(idx int) {
		a.onPlaylistSelectedCustom()
	})

	a.playlistFooter = tview.NewTextView().
		SetDynamicColors(true).
		SetTextAlign(tview.AlignCenter).
		SetTextColor(a.theme.Subtext0)
	a.playlistFooter.SetBackgroundColor(a.theme.Base)
	a.updatePlaylistFooter()

	playlistContainer := a.playlist.GetItem(0)
	a.playlist.Flex.Clear()
	a.playlist.Flex.AddItem(playlistContainer, 0, 1, false)
	a.playlist.Flex.AddItem(a.playlistFooter, 1, 0, false)
}

func (a *SimpleApp) setupDetailsComponent() {
	a.detailsThumb = tview.NewImage().
		SetColors(tview.TrueColor).
		SetDithering(tview.DitheringFloydSteinberg)

	a.detailsText = tview.NewTextView().
		SetDynamicColors(true).
		SetTextAlign(tview.AlignLeft).
		SetTextColor(a.theme.Text).
		SetWordWrap(true)

	a.detailsView = tview.NewFlex().
		SetDirection(tview.FlexColumn).
		AddItem(a.detailsThumb, 20, 0, false).
		AddItem(a.detailsText, 0, 1, false)

	a.detailsView.SetBorder(true).
		SetTitle(" Detalhes ").
		SetBorderColor(a.theme.Surface0)
}

func (a *SimpleApp) setupPlayerComponents() {
	a.thumbnailView = tview.NewImage().
		SetColors(tview.TrueColor).
		SetDithering(tview.DitheringFloydSteinberg)

	a.thumbnailView.SetBorder(false)

	a.playerInfo = tview.NewTextView().
		SetDynamicColors(true).
		SetTextAlign(tview.AlignLeft).
		SetTextColor(a.theme.Text)

	a.playerInfo.SetBorder(false)

	playerContent := tview.NewFlex().SetDirection(tview.FlexColumn).
		AddItem(a.thumbnailView, 20, 0, false).
		AddItem(a.playerInfo, 0, 1, false)

	a.playerBox = tview.NewFlex().SetDirection(tview.FlexRow).
		AddItem(playerContent, 0, 1, false)

	a.playerBox.SetBorder(true).
		SetTitle(" Player ").
		SetBorderColor(a.theme.Surface1)
}

func (a *SimpleApp) setupStatusBars() {
	a.statusBar = tview.NewTextView().
		SetDynamicColors(true).
		SetTextAlign(tview.AlignCenter)

	a.commandBar = tview.NewTextView().
		SetDynamicColors(true).
		SetTextAlign(tview.AlignCenter)

	a.modeBadge = tview.NewTextView().
		SetDynamicColors(true).
		SetTextAlign(tview.AlignRight)

	a.updatePlayerInfo()
	a.updateModeBadge()
	a.statusBar.SetText("")
	a.updateCommandBar()
}

func (a *SimpleApp) setupHelpView() {
	a.helpView = NewHelpView(a.strings, a.version, a.theme, a.app, func() {
		a.inModal = false
		a.app.SetRoot(a.getMainLayout(), true)
		if a.prevFocused != nil {
			a.app.SetFocus(a.prevFocused)
		}
	})
}

func (a *SimpleApp) setupConfigView() {
	a.configForm = tview.NewForm()
	a.configForm.SetBorder(true).SetTitleAlign(tview.AlignCenter)
	a.buildConfigForm()
	a.applyThemeToConfigForm()

	// Centered overlay so the form reads as a modal dialog.
	a.configFlex = tview.NewFlex().
		AddItem(nil, 0, 1, false).
		AddItem(tview.NewFlex().SetDirection(tview.FlexRow).
			AddItem(nil, 0, 1, false).
			AddItem(a.configForm, 17, 0, true).
			AddItem(nil, 0, 1, false), 64, 0, true).
		AddItem(nil, 0, 1, false)
}

// buildConfigForm (re)populates the settings form. Called on first setup and
// whenever the language changes (which alters every label).
func (a *SimpleApp) buildConfigForm() {
	a.configBuilding = true
	defer func() { a.configBuilding = false }()

	form := a.configForm
	form.Clear(true)
	form.SetTitle(" ⚙  " + a.strings.Config + " ")

	// Language
	langs := GetAllLanguages()
	langNames := make([]string, len(langs))
	curLang := 0
	for i, l := range langs {
		langNames[i] = GetLanguageName(l)
		if l == a.language {
			curLang = i
		}
	}
	form.AddDropDown(a.strings.Language, langNames, curLang, func(_ string, idx int) {
		if a.configBuilding || idx < 0 || idx >= len(langs) || langs[idx] == a.language {
			return
		}
		a.applyLanguage(langs[idx])
		a.refreshTitles()
		a.rebuildConfigForm()
		a.setStatus(a.theme.Green, "✓ "+fmt.Sprintf(a.strings.LanguageChanged, GetLanguageName(a.language)))
	})

	// Theme
	themes := GetAllThemes()
	themeNames := make([]string, len(themes))
	curTheme := 0
	for i := range themes {
		themeNames[i] = themes[i].Name
		if themes[i].ID == a.theme.ID {
			curTheme = i
		}
	}
	form.AddDropDown(a.strings.Theme, themeNames, curTheme, func(_ string, idx int) {
		if a.configBuilding || idx < 0 || idx >= len(themes) {
			return
		}
		nt := themes[idx]
		a.theme = &nt
		cfg, _ := config.LoadConfig()
		cfg.Theme.Active = nt.ID
		cfg.Theme.CustomPath = ""
		_ = config.SaveConfig(cfg)
		a.applyTheme()
		a.setStatus(a.theme.Green, "✓ "+fmt.Sprintf(a.strings.ThemeChanged, a.theme.Name))
	})

	// Video quality
	quals := []string{"best", "360", "480", "720", "1080", "tct"}
	qualNames := make([]string, len(quals))
	curQ := 0
	for i, q := range quals {
		qualNames[i] = qualityLabel(q)
		if q == a.videoQuality {
			curQ = i
		}
	}
	form.AddDropDown(a.strings.VideoQuality, qualNames, curQ, func(_ string, idx int) {
		if a.configBuilding || idx < 0 || idx >= len(quals) {
			return
		}
		a.mu.Lock()
		a.videoQuality = quals[idx]
		a.mu.Unlock()
		cfg, _ := config.LoadConfig()
		cfg.Playback.VideoQuality = quals[idx]
		_ = config.SaveConfig(cfg)
		a.setStatusf(a.theme.Green, "✓ "+a.strings.QualityChanged, qualityLabel(quals[idx]))
	})

	// Video codec
	codecs := []string{"", "vp9", "av1"}
	codecNames := make([]string, len(codecs))
	curC := 0
	for i, c := range codecs {
		codecNames[i] = codecLabel(c)
		if c == a.videoCodec {
			curC = i
		}
	}
	form.AddDropDown(a.strings.VideoCodec, codecNames, curC, func(_ string, idx int) {
		if a.configBuilding || idx < 0 || idx >= len(codecs) {
			return
		}
		a.mu.Lock()
		a.videoCodec = codecs[idx]
		a.mu.Unlock()
		cfg, _ := config.LoadConfig()
		cfg.Playback.VideoCodec = codecs[idx]
		_ = config.SaveConfig(cfg)
		a.setStatusf(a.theme.Green, "✓ "+a.strings.CodecChanged, codecLabel(codecs[idx]))
	})

	// Download directory
	form.AddInputField(a.strings.DownloadDir, a.downloadDir, 40, nil, func(text string) {
		if a.configBuilding {
			return
		}
		a.downloadDir = text
	})

	form.AddButton(a.strings.Help, func() {
		a.persistDownloadDir()
		a.configOpen = false
		a.app.SetRoot(a.helpView.Flex, true)
		a.helpView.FocusContent()
	})
	form.AddButton(a.strings.Close, a.closeConfig)

	a.styleConfigItems()
}

// styleConfigItems gives each form field a clear focus indicator. tview.Form
// re-applies field/label colors on every draw (via SetFormAttributes), so
// per-item color changes don't stick — instead we toggle a "▶" marker in the
// label text (which the form leaves untouched). Both states are two cells wide
// so the layout never shifts.
func (a *SimpleApp) styleConfigItems() {
	form := a.configForm
	for i := 0; i < form.GetFormItemCount(); i++ {
		item := form.GetFormItem(i)
		name := strings.TrimSpace(strings.TrimPrefix(item.GetLabel(), "▶"))
		switch w := item.(type) {
		case *tview.DropDown:
			w.SetLabel("  " + name)
			w.SetFocusFunc(func() { w.SetLabel("▶ " + name) })
			w.SetBlurFunc(func() { w.SetLabel("  " + name) })
		case *tview.InputField:
			w.SetLabel("  " + name)
			w.SetFocusFunc(func() { w.SetLabel("▶ " + name) })
			w.SetBlurFunc(func() { w.SetLabel("  " + name) })
		}
	}
}

// rebuildConfigForm re-creates the form (used after a language change) and keeps
// it on screen with focus.
func (a *SimpleApp) rebuildConfigForm() {
	a.buildConfigForm()
	a.applyThemeToConfigForm()
	a.app.SetRoot(a.configFlex, true)
	a.app.SetFocus(a.configForm)
}

func (a *SimpleApp) applyThemeToConfigForm() {
	if a.configForm == nil {
		return
	}
	a.configForm.SetBackgroundColor(a.theme.Base)
	a.configForm.SetBorderColor(a.theme.Blue)
	a.configForm.SetTitleColor(a.theme.Text)
	a.configForm.SetLabelColor(a.theme.Subtext1)
	a.configForm.SetFieldBackgroundColor(a.theme.Surface0)
	a.configForm.SetFieldTextColor(a.theme.Text)
	a.configForm.SetButtonBackgroundColor(a.theme.Surface1)
	a.configForm.SetButtonTextColor(a.theme.Text)
	a.configForm.SetButtonActivatedStyle(tcell.StyleDefault.
		Background(a.theme.Blue).Foreground(a.theme.Base))
}

// closeConfig persists the download directory and returns to the main layout.
func (a *SimpleApp) closeConfig() {
	a.persistDownloadDir()
	a.configOpen = false
	a.inModal = false
	a.app.SetRoot(a.getMainLayout(), true)
	if a.prevFocused != nil {
		a.app.SetFocus(a.prevFocused)
	}
}

func (a *SimpleApp) persistDownloadDir() {
	cfg, _ := config.LoadConfig()
	cfg.Download.Dir = strings.TrimSpace(a.downloadDir)
	_ = config.SaveConfig(cfg)
}

// refreshTitles re-applies translated titles/labels after a language change.
func (a *SimpleApp) refreshTitles() {
	a.searchInput.SetTitle(" " + a.strings.Search + " ")
	a.searchResults.SetTitle(" " + a.strings.Results + " [0] ")
	a.playlist.SetTitle(fmt.Sprintf(" %s [%d] ", a.strings.Playlist, len(a.playlistTracks)))
	a.playerBox.SetTitle(" " + a.strings.Player + " ")
	a.setupHelpView()
	a.updateCommandBar()
	a.updatePlaylistFooter()
	a.updateModeBadge()
	a.updatePlayerInfo()
}

func (a *SimpleApp) setupLayout() {
	searchPanel := tview.NewFlex().SetDirection(tview.FlexRow).
		AddItem(a.searchInput, 3, 0, true).
		AddItem(a.searchResults.Flex, 0, 1, true)

	topFlex := tview.NewFlex().SetDirection(tview.FlexColumn).
		AddItem(searchPanel, 0, 1, true).
		AddItem(a.playlist.Flex, 0, 1, true)

	statusBarFlex := tview.NewFlex().SetDirection(tview.FlexColumn).
		AddItem(a.statusBar, 0, 1, false).
		AddItem(a.modeBadge, 24, 0, false)

	mainLayout := tview.NewFlex().SetDirection(tview.FlexRow).
		AddItem(topFlex, 0, 1, true).
		AddItem(a.playerBox, 5, 0, false).
		AddItem(statusBarFlex, 1, 0, false).
		AddItem(a.commandBar, 1, 0, false)

	a.app.SetRoot(mainLayout, true).SetFocus(a.searchInput)
}

func (a *SimpleApp) getMainLayout() tview.Primitive {
	searchPanel := tview.NewFlex().SetDirection(tview.FlexRow).
		AddItem(a.searchInput, 3, 0, true).
		AddItem(a.searchResults.Flex, 0, 1, true)

	topFlex := tview.NewFlex().SetDirection(tview.FlexColumn).
		AddItem(searchPanel, 0, 1, true).
		AddItem(a.playlist.Flex, 0, 1, true)

	statusBarFlex := tview.NewFlex().SetDirection(tview.FlexColumn).
		AddItem(a.statusBar, 0, 1, false).
		AddItem(a.modeBadge, 24, 0, false)

	return tview.NewFlex().SetDirection(tview.FlexRow).
		AddItem(topFlex, 0, 1, true).
		AddItem(a.playerBox, 5, 0, false).
		AddItem(statusBarFlex, 1, 0, false).
		AddItem(a.commandBar, 1, 0, false)
}

func (a *SimpleApp) setupResizeHandler() {
	var lastW, lastH int
	a.app.SetBeforeDrawFunc(func(screen tcell.Screen) bool {
		w, h := screen.Size()
		if w != lastW || h != lastH {
			lastW, lastH = w, h
			a.searchResults.MarkDirty()
			a.playlist.MarkDirty()
			go a.app.Draw()
		} else {
			a.searchResults.RefreshIfResized()
			a.playlist.RefreshIfResized()
		}
		return false
	})
}

func (a *SimpleApp) setupInputHandlers() {
	a.app.SetInputCapture(func(event *tcell.EventKey) *tcell.EventKey {
		focused := a.app.GetFocus()

		if event.Key() == tcell.KeyCtrlQ {
			a.cleanup()
			a.app.Stop()
			return nil
		}

		if event.Key() == tcell.KeyEsc {
			if a.inModal {
				if a.configOpen {
					a.persistDownloadDir()
					a.configOpen = false
				}
				a.inModal = false
				a.app.SetRoot(a.getMainLayout(), true)
				if a.prevFocused != nil {
					a.app.SetFocus(a.prevFocused)
				}
				return nil
			}
		}

		if event.Key() == tcell.KeyCtrlC {
			a.prevFocused = focused
			a.inModal = true
			a.configOpen = true
			a.buildConfigForm()
			a.applyThemeToConfigForm()
			a.app.SetRoot(a.configFlex, true)
			a.app.SetFocus(a.configForm)
			return nil
		}

		if event.Key() == tcell.KeyCtrlD {
			if !a.inModal {
				go func() {
					track := a.getContextTrack(focused)
					if track == nil {
						a.app.QueueUpdateDraw(func() {
							a.setStatus(a.theme.Yellow, "⚠ "+a.strings.NoTrackSelected)
						})
						return
					}
					a.downloadTrack(*track)
				}()
			}
			return nil
		}

		if a.inModal {
			return event
		}

		if event.Rune() == '?' && focused != a.searchInput {
			a.inModal = true
			a.prevFocused = focused
			a.app.SetRoot(a.helpView.Flex, true)
			a.helpView.FocusContent()
			return nil
		}

		if focused == a.searchInput {
			if event.Key() == tcell.KeyTab {
				a.app.SetFocus(a.searchResults.Flex)
				a.updateCommandBar()
				return nil
			}
			return event
		}

		switch event.Key() {
		case tcell.KeyTab:
			switch focused {
			case a.searchResults.Flex:
				a.app.SetFocus(a.playlist.Flex)
				a.updateCommandBar()
			case a.playlist.Flex:
				a.app.SetFocus(a.playerBox)
				a.updateCommandBar()
			case a.playerBox:
				a.app.SetFocus(a.searchInput)
				a.updateCommandBar()
			}
			return nil
		}

		return a.handleKeyPress(event, focused)
	})
}

func (a *SimpleApp) applyTheme() {
	tview.Styles.PrimitiveBackgroundColor = a.theme.Base
	tview.Styles.ContrastBackgroundColor = a.theme.Surface0
	tview.Styles.MoreContrastBackgroundColor = a.theme.Surface1
	tview.Styles.BorderColor = a.theme.Surface0
	tview.Styles.TitleColor = a.theme.Text
	tview.Styles.GraphicsColor = a.theme.Blue
	tview.Styles.PrimaryTextColor = a.theme.Text
	tview.Styles.SecondaryTextColor = a.theme.Subtext1
	tview.Styles.TertiaryTextColor = a.theme.Subtext0
	tview.Styles.InverseTextColor = a.theme.Base
	tview.Styles.ContrastSecondaryTextColor = a.theme.Subtext0

	a.searchInput.SetFieldBackgroundColor(a.theme.Surface0).
		SetFieldTextColor(a.theme.Text).
		SetBorderColor(a.theme.Blue)

	a.searchResults.SetTheme(a.theme)
	a.playlist.SetTheme(a.theme)

	a.playerBox.SetBorderColor(a.theme.Surface1)

	a.statusBar.SetBackgroundColor(a.theme.Base)
	a.statusBar.SetTextColor(a.theme.Text)

	a.commandBar.SetBackgroundColor(a.theme.Base)
	a.commandBar.SetTextColor(a.theme.Subtext1)

	a.modeBadge.SetBackgroundColor(a.theme.Base)
	a.modeBadge.SetTextColor(a.theme.Mauve)

	a.playlistFooter.SetBackgroundColor(a.theme.Base)
	a.playlistFooter.SetTextColor(a.theme.Subtext0)

	a.playerInfo.SetBackgroundColor(a.theme.Base)
	a.playerInfo.SetTextColor(a.theme.Text)

	a.detailsText.SetBackgroundColor(a.theme.Base)
	a.detailsText.SetTextColor(a.theme.Text)
	a.detailsView.SetBorderColor(a.theme.Surface0)

	// The help view bakes theme colors into its text at construction, so rebuild
	// it to pick up the new palette in real time.
	a.setupHelpView()

	a.applyThemeToConfigForm()

	a.updateCommandBar()
	a.updatePlaylistFooter()
	a.updateModeBadge()
	a.updatePlayerInfo()
}

func qualityLabel(q string) string {
	if q == "best" || q == "" {
		return "Best"
	}
	if q == "tct" {
		return "Terminal"
	}
	return q + "p"
}

func codecLabel(c string) string {
	switch c {
	case "vp9":
		return "VP9"
	case "av1":
		return "AV1"
	default:
		return "Any"
	}
}

func (a *SimpleApp) initLanguageFromConfig() {
	cfg, _ := config.LoadConfig()

	lang := parseLanguage(cfg.UI.Language)
	if lang == "" {
		lang = LanguagePT
	}

	a.applyLanguage(lang)
}

func parseLanguage(s string) Language {
	s = strings.ToLower(strings.TrimSpace(s))
	switch {
	case s == "en", strings.HasPrefix(s, "en-"), strings.HasPrefix(s, "en_"):
		return LanguageEN
	case s == "pt", strings.HasPrefix(s, "pt-"), strings.HasPrefix(s, "pt_"), s == "br":
		return LanguagePT
	default:
		return LanguagePT
	}
}

func (a *SimpleApp) applyLanguage(lang Language) {
	a.language = lang
	a.strings = GetStrings(lang)

	cfg, _ := config.LoadConfig()
	cfg.UI.Language = string(lang)
	_ = config.SaveConfig(cfg)

	search.SetTexts(search.Texts{
		EmptyQuery:       a.strings.EmptyQuery,
		NoResultsFor:     a.strings.NoResultsFor,
		YtDlpNotFound:    a.strings.YtDlpNotFound,
		YtDlpStartFailed: a.strings.YtDlpStartFailed,
		YtDlpError:       a.strings.YtDlpError,
		UnknownDate:      a.strings.UnknownDate,
		NoDescription:    a.strings.NoDescription,
	})
}
