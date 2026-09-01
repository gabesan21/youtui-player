# Skill — build

- **Project:** [[pop/PROJECT|youtui-player]]
- **When to use:** you need to compile the project binary from the local fork.

## Procedure

1. Ensure you are in the repository root (where the `Makefile` is).
2. Run `make build`.
   - This first runs `make deps`, which executes `go mod download` and `go mod tidy`.
   - It then compiles with `go build -ldflags "-X main.Version=$(VERSION) -s -w" -o youtui-player .`.
   - `VERSION` comes from `git describe --tags --always --dirty`; if git is unavailable, it falls back to `dev`.
3. Verify the output: a `./youtui-player` binary should exist.
4. Optional: run `make version` to print the version string that was injected.
5. Optional: run `make clean` to remove the compiled binary and run `go clean`.

## Caveats

- `make build` depends on the `deps` target, so it mutates `go.mod`/`go.sum` via `go mod tidy`.
- The `-s -w` ldflags strip debug info; if you need symbols for debugging, build directly with `go build`.
- `make clean` only removes `./youtui-player` from the repo root; installed copies under `DESTDIR`/`PREFIX` are handled by `make uninstall`.
- Do not invent Makefile targets such as `make build-all`; only `build`, `deps`, `clean`, and `version` exist for compilation/versioning.

## Example

```bash
make build
./youtui-player --help
make clean
```
