# Epoch 1 — Organization

- **Project:** [[pop/PROJECT|youtui-player]] · **Roadmap:** [[pop/ROADMAP|Roadmap]]
- **Status:** completed
- **Description:** Knowledge harness faithful to the existing code: DOX tree, operational skills, notes and research.

## Recon and forks

- [[pop/notes/decisions/2026-09-01-personal-fork|2026-09-01 personal fork]] — resolved at import: personal fork, never published to AUR; old-repo references and AUR flows are removed in [[pop/roadmap/2-fork-adaptation|Epoch 2]].
- [x] RECON NEEDED: historical design decisions captured in task 1.3.1:
  - [[pop/notes/decisions/2026-09-01-no-ci-manual-verification|no CI, manual verification]]
  - [[pop/notes/decisions/2026-09-01-socat-shell-pipe-mpv-ipc|socat/shell-pipe mpv IPC]]
  - [[pop/notes/decisions/2026-09-01-yt-dlp-subprocess-search|yt-dlp subprocess search]]

## Phase 1.1 — Project map (DOX)

- **Status:** in progress
- **Description:** DOX tree initialization over the existing Go code.

| Task | Description (≤1 line) | Status |
|------|-----------------------|--------|
| [[1.1.2-phase-verification]] | Runs the phase suite: DOX contracts consistent with the tree, links and hashes valid. · size: S | 003_human_approval |

## Phase 1.2 — Operational skills

- **Status:** in progress
- **Description:** `pop/skills/` entries for build, test, run and local install, faithful to the Makefile and PKGBUILD.

| Task | Description (≤1 line) | Status |
|------|-----------------------|--------|
| [[1.2.2-phase-verification]] | Validates each skill by executing its commands read-only where possible. · size: S | 003_human_approval |

## Phase 1.3 — Notes and research

- **Status:** completed
- **Description:** Decisions, references and open research recorded; resolves this epoch's RECON NEEDED item.

| Task | Description (≤1 line) | Status |
|------|-----------------------|--------|
| [[1.3.2-phase-verification]] | Checks notes against code reality and closes the epoch status. · size: S | 003_human_approval |
