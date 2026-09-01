# Epoch 1 — Organization

- **Project:** [[pop/PROJECT|youtui-player]] · **Roadmap:** [[pop/ROADMAP|Roadmap]]
- **Status:** pending
- **Description:** Knowledge harness faithful to the existing code: DOX tree, operational skills, notes and research.

## Recon and forks

- [[pop/notes/decisions/2026-09-01-personal-fork|2026-09-01 personal fork]] — resolved at import: personal fork, never published to AUR; old-repo references and AUR flows are removed in [[pop/roadmap/2-fork-adaptation|Epoch 2]].
- [x] RECON NEEDED: historical design decisions captured in task 1.3.1:
  - [[pop/notes/decisions/2026-09-01-no-ci-manual-verification|no CI, manual verification]]
  - [[pop/notes/decisions/2026-09-01-socat-shell-pipe-mpv-ipc|socat/shell-pipe mpv IPC]]
  - [[pop/notes/decisions/2026-09-01-yt-dlp-subprocess-search|yt-dlp subprocess search]]

## Phase 1.1 — Project map (DOX)

- **Status:** pending
- **Description:** DOX tree initialization over the existing Go code.

| Task | Description (≤1 line) | Status |
|------|-----------------------|--------|
| `1.1.1-dox-tree-initialization` | Recursive sweep of the Go code; root DOX rail + child contracts only where a trigger exists; human curation at gate 003. · size: L | not started |
| `1.1.2-phase-verification` | Runs the phase suite: DOX contracts consistent with the tree, links and hashes valid. · size: S | not started |

## Phase 1.2 — Operational skills

- **Status:** pending
- **Description:** `pop/skills/` entries for build, test, run and local install, faithful to the Makefile and PKGBUILD.

| Task | Description (≤1 line) | Status |
|------|-----------------------|--------|
| `1.2.1-build-test-run-skills` | pop/skills/ entries for build, fmt/vet/test (incl. -short vs live tests), run and local Arch install (makepkg -si), faithful to the Makefile/PKGBUILD. · size: M | not started |
| `1.2.2-phase-verification` | Validates each skill by executing its commands read-only where possible. · size: S | not started |

## Phase 1.3 — Notes and research

- **Status:** pending
- **Description:** Decisions, references and open research recorded; resolves this epoch's RECON NEEDED item.

| Task | Description (≤1 line) | Status |
|------|-----------------------|--------|
| `1.3.1-decisions-and-references` | Git/code mining into pop/notes/decisions/ and references/; resolves this epoch's RECON NEEDED item. · size: M | not started |
| `1.3.2-phase-verification` | Checks notes against code reality and closes the epoch status. · size: S | not started |
