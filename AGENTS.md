# youtui-player — instructions for agents

> Project managed by the **ProjectOfProjects (PoP)** workflow. `CLAUDE.md` is a symlink to this file — always edit this one.

- **Scope:** this directory is the entire scope of the flow — the harness travels with it and **nothing above this root belongs to it**, even when a tool loads an ancestor `AGENTS.md` on its own ("Current scope" section of [[WORKFLOW|WORKFLOW]]).
- **Project language:** en — specs, notes, researches, code comments and the entire kanban flow follow this language. **Supported languages (i18n):** pt and en — auto-detected from the locale.
- **Type:** uni-repo — this folder **is** the repository itself, with the entire `pop/` inside it.
- **Profile:** [[pop/PROJECT|PROJECT]] · **Roadmap:** [[pop/ROADMAP|ROADMAP]] · **Modifications:** [[pop/MODIFICATIONS|MODIFICATIONS]] (created on demand)

## What does NOT go in this file

Single source: what lives in the harness is never copied here, because duplication is guaranteed drift — the flow changes and the copy starts lying. **Never** write here:

- narration of the kanban stages (names, order, what each one does) — only [[WORKFLOW|WORKFLOW]];
- the context protocol and any reading/search heuristic — [[WORKFLOW|WORKFLOW]] and the skills;
- general flow rules (optional kanban with tracking always, memory/lean roadmap, sovereignty of the human command) — the "Transversal rules" section of [[WORKFLOW|WORKFLOW]], which the installer delivers alongside the harness;
- any copyable excerpt of [[WORKFLOW|WORKFLOW]] — link it with a trigger instead of reproducing it.

Only what belongs to **this project** goes here: language, repos and PR branch, skills and verification commands, DOX. **Cap: ~60 lines** — the only exception is the DOX section of applications.

## Repositories

| Repo | URL | Clone at | PR branch |
|------|-----|----------|-----------|
| youtui-player | https://github.com/gabesan21/youtui-player | the project root itself **is** the repo | main |

## Workflow

Content changes enter through triage: direct fix, the **no-kanban route** (the coding agent's plan mode, mandatory `D-` memory) or the kanban in `pop/kanban/` — recommended for large changes and the default for yolo and for roadmap (`<n>.<m>.<t>-<slug>`) or modifications (`M-<n>.<t>-<slug>`) items.

- A change request with no card triggers `new-task` → `advance-task`; "start the flow in yolo" materializes/releases the task and follows the entire yolo route, never direct execution.
- **Delivery:** the task PR targets the **PR branch declared** in the repositories table above; the merge is always the human's.
- **Stages, gates, yolo route and context protocol:** [[WORKFLOW|WORKFLOW]] is the single source — read it before creating, advancing, verifying or closing any task of this project, and do not replicate any of it here.

## Skills

- **PoP workflow:** `.agents/skills/` — `new-task`, `advance-task`, `judge-dredd`, `plan-roadmap`, `write-spec`, `sync-specs`, `optimize-memory`.
- **Project domain:** `pop/skills/` — listed in the profile [[pop/PROJECT|PROJECT]].

### Clean code (code projects only)

- `clean-code-change` (`.agents/skills/`) — follow when **planning (002) and executing (004)** any task that creates or changes code.
- `clean-code-review` (`.agents/skills/`) — follow when **verifying (005)** a code task and as a reading criterion in plan or PR gates.
- **Mandatory:** in 002, every task that creates/changes code enters `clean-code-change` on the **004** row and `clean-code-review` on the **005** row of the card's **Skills per stage** table.

#### Project verification

| Check | Command |
|-------|---------|
| Formatter | `make fmt` |
| Linter | `make vet` |
| Tests | `make test` |

## DOX process — hierarchical agent context in the code

> PoP standard for **application** (programming) projects. **Self-contained** model, inspired by the open DOX framework (agent0ai/dox, MIT) — PoP does not depend on the original repository. The child contracts live alongside the code.

### What it is

A tree of `AGENTS.md` files inside the code: the one at the code root is the **DOX rail** — rules for the whole project + high-level index; each relevant directory has its own, with local rules and an index of its own subtree. Each `AGENTS.md` is a **binding work contract for its subtree**: no blind edits, no stale documentation.

### Rules

1. **Before editing:** read the code's root AGENTS.md, identify **all** affected paths and **walk the tree** down to each edit location, reading every applicable AGENTS.md along the way. The walk can be delegated to a subagent that returns **only the rules applicable** to the task's paths — the executor receives the extract, not the tree.
2. **Local understanding:** any point in the code must be understandable by reading only the nearest AGENTS.md + all its parents above it. If it isn't, a contract is missing — create/complete the local one before editing.
3. **Conflicts:** the nearest document rules over local details; a child **never weakens** a parent's directive.
4. **Operational concision:** broad rules at the high levels, concrete detail in the children. Only what changes editing decisions — no prose. **Polarity:** prefer negative constraints ("never X in this subtree") and conditionals ("if Y, then Z"); avoid generic positive guidance ("follow the style") — guardrails yield +13.8pp accuracy, generic guidance −6.4pp. Cap: **~60 lines** per subtree contract; overflowed, the detail moves down into a child. Exception: a large-tree directory (many subfolders) may exceed it to hold the subtree's index — the exception covers the index, not prose.
5. **Mandatory review:** every relevant change requires reviewing the affected AGENTS.md files — update them when purpose, scope, responsibility, structure, flows, inputs, outputs or quality standards change.
6. **Closeout:** when finishing the work, re-check the changed paths, update the owning document and the affected parents, refresh the indexes, remove obsolete content and run the pertinent checks.
7. **Related contracts:** optional section in each contract with relative markdown links (`../services/payments/AGENTS.md`) to contracts of other subtrees that local decisions depend on — each link with a 1-line **trigger** (*when to follow it*). Max. **~3 laterals (ideally 0-2)** and **<7 total references** per contract (laterals + skills + children index); only a dependency that changes an editing decision (not every import); a link without a trigger doesn't count. Need more? A sign of coupling, or of routing that belongs in the parent's index. The walk becomes: vertical down to the edit location + the laterals whose trigger matches the task. The closeout (rule 6) also updates the laterals of the touched contracts. **Contract→spec link:** when the harness lives in the same repository as the code, the contract may link the theme's **spec** by relative markdown path (`pop/specs/<spec>.md`), with a trigger and counting toward the reference cap; when the harness lives outside the repository, the contract↔spec bridge is the task's card/plan — the harness does not resolve from inside the repo (the spec→contract direction always exists, in the spec template).
8. **Subtree skills:** a contract may link project skills (`pop/skills/`) **specific to that folder** — a procedure that changes how the subtree is edited (e.g. `migrations/` links the migration skill with the trigger "follow before creating/changing any migration"). Always a link with a trigger, never a copy of the content (copy = drift). **Workflow** skills (advance-task etc.) never go into a contract — they belong to the card's "Skills per stage" table: the card answers "how do I work this task"; the contract answers "what holds when editing this folder, whatever the task". Skill links count toward rule 7's reference cap.
9. **Verifiable citations:** a contract that cites a concrete file or code excerpt may pin the citation with the annotation `<!-- pop-hash: <relative-path> sha256=<hash of the cited file> -->` (HTML comment, invisible; path relative to the contract's folder; hash via `sha256sum <file>`). `pop_validate` recomputes it **fail-closed** — cited file gone or changed → violation — wherever the scope reaches the file (repos and clones present at the scope root). When revising the citation, update the hash: the violation message prints the new one.

### Initialization

Code without a DOX tree → recursive sweep and tree construction: root AGENTS.md with the general index and child contracts **only where there is an objective trigger** — do not create empty AGENTS.md files "just in case". In an imported project (`import-project`), initialization is a task of Epoch 1 (Organization).

- **Child-contract triggers:** ≥2 non-obvious conventions; a previous blind-edit error; a stack different from the rest of the repo; different ownership (another team/owner); distinct security/permission rules; legacy code.
- **The tree is born lean:** initial contracts of **20–30 lines**, growing toward the ~60 cap as real need appears; the root passed ~150 lines → move detail down into a child. Reference scale: **5–15 contracts** are enough for most repos.
- **Mandatory human curation:** the initial tree goes through gate 003 of the task that creates it — an LLM-generated contract without curation **worsens** the result (−3% success, +23% cost).

### In the PoP flow

- **002 (brief):** the planner identifies contracts applicable to likely areas and links them; broad walking happens only when a decision depends on it.
- **004:** each front walks the tree to its edit location before its first change. Reuse an extract if base/hash is unchanged; changed contracts join the delivery.
- **005:** the reviewer checks whether changes to purpose, structure, flows or rules updated contracts; no-impact changes require no rewrite.
- **A repo that must stay clean of AI files:** decide with the user in the interview — commit the DOX tree to the repo (PoP default) or keep only the root contract in the project's AGENTS.md, outside the repository.

### DOX root rail — youtui-player technical contract

Rules and facts that hold for the whole codebase:

- **Stack:** Go 1.24 (toolchain `go1.24.7`, per `go.mod`). Deps: `github.com/rivo/tview`, `github.com/gdamore/tcell/v2` v2.7.4, `github.com/BurntSushi/toml` v1.5.0, `github.com/nfnt/resize`. No database, no queue, no external API service — the app shells out to local CLI tools. Module: `github.com/IvelOt/youtui-player` (Epoch 2 renames it to `gabesan21`). Packaged for Arch Linux via `PKGBUILD` — inherited from upstream; this fork is **never published** to the AUR (`PKGBUILD` stays for local `makepkg -si` install only).
- **Commands:** `make build` (compile) · `make run` (build and run) · `make test` (`go test ./...`; test files exist under `internal/ui/`) · `make fmt` · `make vet` · `make check-deps` (verify runtime deps) · `make clean` · `make deps`. Single test: `go test ./internal/... -run TestName`. No CI config — builds/tests/releases are manual (see `PKGBUILD`).
- **Runtime dependencies (never stub them silently):** `mpv` (media player backend), `yt-dlp` (YouTube search/extraction), `socat` (IPC with mpv via Unix socket), `ffmpeg` (audio→MP3 extraction and video→MP4 merge on download).
- **Concurrency (binding):** `SimpleApp.mu` (sync.Mutex) guards shared state. All UI mutations must go through `app.QueueUpdateDraw()`; background goroutines (playback, thumbnail fetching, search) must never touch UI primitives directly.
- **Package layout:** `internal/ui/` — main TUI layer: central `SimpleApp` struct (`app.go`) owns all state and UI components; wiring in `setup.go`; input handling in `handlers.go`; custom `CustomList` widget (`custom_list.go`) extends tview with thumbnails. `internal/search/` — YouTube search implemented in `invidious.go` as a `yt-dlp` subprocess; JSON parsed into `Result` structs; entry points `SearchVideos()`, `GetPlaylistVideos()`, `GetVideoDetails()`. `internal/config/` — TOML config and JSON session state.
- **Data flow:** search → `search.SearchVideos()` spawns `yt-dlp`, returns `[]Result`; playback → `playTrackSimple()` spawns `mpv` with `--input-ipc-server`, progress polled via `socat` on the IPC socket; state auto-saved to JSON after changes and restored on startup (`PlayerState` persists search term/results, playlist, scroll positions, current page, play modes).
- **XDG paths (all optional, hardcoded fallbacks):** `XDG_CONFIG_HOME` → `~/.config` (`internal/config/config.go`, config at `~/.config/youtui-player/youtui.conf`) · `XDG_STATE_HOME` → `~/.local/state` (`state.go`, session at `~/.local/state/youtui-player/state.json`) · `XDG_CACHE_HOME` → `~/.cache` (`internal/ui/thumbnail.go`) · `XDG_DATA_HOME` → `~/.local/share` (`internal/ui/download.go`) · `XDG_DOWNLOAD_DIR` → `~/Downloads` (`download.go`) · `LC_ALL`/`LC_MESSAGES`/`LANG` → **Portuguese (`pt`) fallback**, not English (`en`) (`internal/config/config.go`). Reference copy in `.env.example`. No secrets or required env vars.
- **i18n:** `internal/ui/i18n.go` provides PT and EN string packs, auto-detected from `LC_ALL`/`LANG` or the config file; language changes apply in real time via `applyLanguage()`. `search.SetTexts()` is the cross-package bridge that keeps `internal/search` error messages in the active UI language.
- **Themes:** four built-in Catppuccin variants (Latte, Frappé, Macchiato, Mocha), a `Terminal` theme inheriting the host palette (`tcell.ColorDefault` + ANSI accents), plus custom TOML themes. `colorTag()` emits `-` (reset) for `ColorDefault`. `applyTheme()` rebuilds `HelpView` (`setupHelpView()`) because it bakes theme colors at construction. Palette format in `THEMES.md`.
- **Playback config:** `[playback]` TOML section — `default_mode` (`"audio"`/`"video"`), `video_quality` (`"best"`, `"360"`, `"480"`, `"720"`, `"1080"`, `"tct"` terminal video), `video_codec` (`""`, `"vp9"`, `"av1"`). Editable live in the settings view (Ctrl+C, `buildConfigForm()` in `setup.go`; `styleConfigItems()` marks focus with `▶` because `tview.Form` re-applies field colors every draw). Translated into `--ytdl-format` by `buildYtdlFormat()` in `player.go`; `tct` only applies in video mode.
- **Download:** Ctrl+D downloads the context track (`getContextTrack()`: playing track > focused list item) via `yt-dlp` with `--newline --progress-template`; a scanner goroutine renders progress via `renderProgressBar()`. `[download]` config has one option, `dir` (supports `~/`, falls back to `$XDG_DOWNLOAD_DIR` then `~/Downloads`). `buildDownloadFormat()` mirrors playback settings, except `tct` falls back to 360p. Audio-only → MP3 (`-x --audio-format mp3`); video → MP4 (`--merge-output-format mp4`) — both require `ffmpeg`. The `Y` key shows the track URL in a modal and writes it to `$XDG_DATA_HOME/youtui-player/last_url.txt`.
- **Health check:** `health_check.go` checks the installed `yt-dlp` version at startup and warns if it is more than 14 days old.
- **Live tests:** `internal/ui/player_live_test.go` contains `TestMpvPlaysLiveVideoWithAndroidClient`, a real network integration test against YouTube; it is skipped under `-short` and when `mpv`/`yt-dlp`/`ffmpeg` are missing, so `go test ./...` stays green offline.

#### Child contracts

- `internal/ui/AGENTS.md` — follow when editing the TUI layer, event handlers, theme/language wiring or any goroutine that touches UI primitives.
- `internal/search/AGENTS.md` — follow when editing the `yt-dlp` subprocess search, result parsing or i18n bridge.
- `internal/config/AGENTS.md` — follow when editing TOML config, JSON session state, XDG path resolution or locale defaults.

## Essential rules

- Content in the language declared above; wikilinks for internal references; files ≤~150 lines; dates YYYY-MM-DD.
- **Never** check `- [ ] Done` or execute `(user)` items — those belong exclusively to the human.
- **Never** merge a task PR — merging is the human's job (or commanded by them in the merge round).
- **General flow rules** — optional kanban with tracking always, memory + lean roadmap at close-out, sovereignty of the human command with no implicit waiver: the "Transversal rules" section of the [[WORKFLOW|WORKFLOW]] installed alongside this harness. *Never an AGENTS.md inherited from an ancestor directory.* *Read it before acting outside a task or before reading a request as a waiver of the flow.*
- **Imported project:** until Epoch 1 (Organization) is `completed` in the ROADMAP, no task may change the project's content (the folder root) or the repository — only the harness in `pop/` (DOX map, skills, researches, notes). A change request during this period → record it in `pop/notes/ideas/` or as a future-epoch task, explaining the gate.
