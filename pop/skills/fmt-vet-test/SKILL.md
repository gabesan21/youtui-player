# Skill — fmt-vet-test

- **Project:** [[pop/PROJECT|youtui-player]]
- **When to use:** you want to format, vet, or run tests before committing changes.

## Procedure

1. Ensure you are in the repository root.
2. Run `make fmt` to format all Go code with `go fmt ./...`.
3. Run `make vet` to analyze all Go code with `go vet ./...`.
4. Run `make test` to execute the full test suite with `go test ./...`.
   - This runs **every** test, including the live network integration test in `internal/ui/player_live_test.go` if its preconditions are met.
5. To skip the live network integration test, use the direct Go command:
   - `go test -short ./...`
   - There is **no Makefile target** for `-short`; the roadmap's "-short vs live" split is implemented only in the test code via `testing.Short()`.
6. To run a single test by name, use `go test ./internal/... -run TestName` (or any package path).

## Caveats

- `make test` is equivalent to `go test ./...`; it does not accept flags like `-short` or `-run`.
- The live test `TestMpvPlaysLiveVideoWithAndroidClient` is skipped in `-short` mode and also skipped when `mpv`, `yt-dlp`, or `ffmpeg` are not on `PATH`, so `go test ./...` stays green offline.
- `make vet` exists as a target but is missing from the `.PHONY` line in the Makefile; this is a pre-existing nit and does not affect execution.
- Never claim a `make test-short` or similar target — it does not exist.

## Example

```bash
make fmt
make vet
make test

# Skip the live network test
go test -short ./...

# Run only one test
go test ./internal/ui -run TestYtdlPlayerClientArgValue
```
