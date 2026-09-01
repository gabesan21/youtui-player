# Epoch 1 — Organization

- **Project:** [[pop/PROJECT|youtui-player]] · **Roadmap:** [[pop/ROADMAP|Roadmap]]
- **Status:** pending
- **Description:** Knowledge harness faithful to the existing code: DOX tree, operational skills, notes and research.

## Recon and forks

- [ ] RECON NEEDED: whether this repo is a fork of IvelOt/youtui-player or the new canonical home (module path and PKGBUILD still point to IvelOt) — check: human decision recorded in task 1.3.1 notes.
- [ ] RECON NEEDED: historical design decisions (no CI, socat/shell-pipe mpv IPC, yt-dlp subprocess search) — check: interview captured in task 1.3.1.
- [ ] RECON NEEDED: release/AUR strategy for the gabesan21 repo (PKGBUILD sources the upstream IvelOt tarball) — check: decision in task 1.3.1, reflected in the release skill of 1.2.

## Phase 1.1 — Project map (DOX)

- **Status:** pending
- **Description:** DOX tree initialization over the existing Go code.

| Task | Description (≤1 line) | Status |
|------|-----------------------|--------|
| `1.1.1-dox-tree-initialization` | Recursive sweep of the Go code; root DOX rail + child contracts only where a trigger exists; human curation at gate 003. · size: L | not started |
| `1.1.2-phase-verification` | Runs the phase suite: DOX contracts consistent with the tree, links and hashes valid. · size: S | not started |

## Phase 1.2 — Operational skills

- **Status:** pending
- **Description:** `pop/skills/` entries for build, test, run and release, faithful to the Makefile and PKGBUILD.

| Task | Description (≤1 line) | Status |
|------|-----------------------|--------|
| `1.2.1-build-test-run-skills` | pop/skills/ entries for build, fmt/vet/test (incl. -short vs live tests) and run, faithful to the Makefile. · size: M | not started |
| `1.2.2-release-aur-skill` | pop/skills/ entry for versioning and AUR packaging (PKGBUILD/.SRCINFO), pending the 1.3.1 decision. · size: M | not started |
| `1.2.3-phase-verification` | Validates each skill by executing its commands read-only where possible. · size: S | not started |

## Phase 1.3 — Notes and research

- **Status:** pending
- **Description:** Decisions, references and open research recorded; resolves this epoch's RECON NEEDED items.

| Task | Description (≤1 line) | Status |
|------|-----------------------|--------|
| `1.3.1-decisions-and-references` | Interview + git mining into pop/notes/decisions/ and references/; resolves the RECON NEEDED items of this epoch. · size: M | not started |
| `1.3.2-phase-verification` | Checks notes against code reality and closes the epoch status. · size: S | not started |
