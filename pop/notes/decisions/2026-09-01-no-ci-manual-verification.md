---
author: agent
created: 2026-09-01
---

# No CI — manual verification only

Origin: task 1.3.1-decisions-and-references.

## Question
Why does the project rely on manual build/test verification instead of continuous integration?

## Observed facts

- No CI configuration files exist in the repository root:
  - `.github/` — absent
  - `.gitlab-ci.yml` — absent
  - `.travis.yml` — absent
  - No other `.yml`/`.yaml` CI configs at the repository root
- `git log --all --oneline -- '.github' '.gitlab-ci.yml' '.travis.yml'` returns no entries; none of these paths have ever been committed in the 64-commit history.
- `Makefile` defines manual quality targets:
  - `make fmt` (`go fmt ./...`) at `Makefile:93-94`
  - `make vet` (`go vet ./...`) at `Makefile:96-97`
  - `make test` (`go test ./...`) at `Makefile:90-91`
  - `make check-deps` verifies runtime binaries (`mpv`, `yt-dlp`, `socat`, `ffmpeg`) at `Makefile:99-103`
- `PKGBUILD` is present but is a local Arch packaging file (`makepkg -si`), not an automated release pipeline; it still points upstream to `IvelOt/youtui-player` and is scheduled for fork cleanup in [[pop/roadmap/2-fork-adaptation|Epoch 2]].

## Inference

The upstream author chose a manual workflow because the project is a small, personal TUI with runtime dependencies on local CLI tools (`mpv`, `yt-dlp`, `socat`, `ffmpeg`) that are hard to exercise faithfully in a generic CI runner without mocking the entire playback/search stack. The verification surface is intentionally left to `make fmt/vet/test` plus local `PKGBUILD` install checks.

## Consequences

- Every change must be verified locally with `make fmt && make vet && make test` before commit.
- The `PKGBUILD` must be validated by hand on Arch when it changes.
- No automated release artifacts are produced; releases are personal-only and remain the human's responsibility.
