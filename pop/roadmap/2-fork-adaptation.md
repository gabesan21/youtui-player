# Epoch 2 — Fork adaptation

- **Project:** [[pop/PROJECT|youtui-player]] · **Roadmap:** [[pop/ROADMAP|Roadmap]]
- **Status:** pending
- **Description:** Make the fork fully personal: old-repo references removed, README states the fork reason, AUR publication flows gone.
- **Abort/pause if:** Epoch 1 (Organization) is not `completed` — the organization gate blocks content changes until then.

## Recon and forks

- [[pop/notes/decisions/2026-09-01-personal-fork|2026-09-01 personal fork]] — the decision that grounds this epoch: personal fork, never published to AUR.

## Phase 2.1 — Fork cleanup

- **Status:** pending
- **Description:** Remove every reference to the upstream repo, except the fork note in the README.

| Task | Description (≤1 line) | Status |
|------|-----------------------|--------|
| `2.1.1-remove-old-repo-references` | go.mod module path + imports → `github.com/gabesan21/youtui-player`; fix clone URLs and upstream references outside the README. · size: M | not started |
| `2.1.2-readme-fork-reason` | README rewritten to state why the fork exists (personal use) — the only remaining reference to `IvelOt/youtui-player`. · size: S | not started |
| `2.1.3-remove-aur-publication` | Delete `.SRCINFO` and the AUR badge/references; PKGBUILD becomes local-install only (`makepkg -si`). · size: S | not started |
| `2.1.4-phase-verification` | `make build/fmt/vet/test` green; grep proves no `IvelOt` reference outside the README fork note. · size: S | not started |
