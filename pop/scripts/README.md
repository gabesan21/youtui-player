# PoP scripts

Python 3.9+, standard library only.

**Task ids:** two origins — roadmap `1.2.3-slug` (`<epoch>.<phase>.<task>`) and modifications `M-1.2-slug` (task `2` of modification `M-1`; frontmatter with `origin: modifications` + `modification: M-1`, no `epoch`/`phase`).

| Script | Purpose |
|---|---|
| `pop_status.py` | Kanban overview, pending gates, claims, circuit breakers, stale work, and merge waits. |
| `pop_claim.py` | Per-task lease preventing duplicate orchestrators. |
| `pop_validate.py` | Validates limits, the freshness of the harness installed in the projects (`content_sha` stamp vs. source — stale is a violation), cards (frontmatter per origin: roadmap requires `epoch`/`phase`; modifications requires `modification: M-<n>`), canonical specs, telemetry, standalone anatomy, links, hashes, and completed-task residue in the roadmap/modifications. |
| `pop_move.py` | Moves a task, updates card/log/telemetry, counts yolo returns, and opens the circuit on failure three. Non-critical yolo transits 002→004 directly (003 only for `critical: true`). A return leaving `005_closing` records the cause in `return_kind`: `--return-kind lacuna\|premissa` is required for →002; →004 assumes `execucao`. In yolo it validates the `.verify.md`'s `pop-verdict`/`pop-delta` markers (approval is terminal; a `pontual=true` delta → directed repair; a return requires a delta), records `return_base` and refuses a 004→005 reentry with no diff on the delta's `paths`. |
| `pop_task.py` | Creates a task card from the template, filling the frontmatter block of the id's origin (roadmap or `M-`). |
| `pop_worktree.py` | Resolves route and manages task worktrees; a local scope refuses them, external yolo starts from the repo's current working branch and the final PR is opened only on human request. |
| `pop_roadmap.py` | At the close of `005_closing`, `close` removes exactly one completed task row from the epoch or modification file after canonical memory; for a single-task modification it removes only the wikilink from the `MODIFICATIONS.md` row. `check/prune` audit/migrate residue. |
| `pop_yolo.py` | Safe waves up to three, verification mode, minimal telemetry, and human circuit reset. `verify-mode` picks `full` only for `critical` or a `premissa` return; on other returns the differential covers the delta. `telemetry` sums the returns per cause (`returns_lacuna\|premissa\|execucao`). |
| `pop_delivery.py` | Idempotent external-yolo integration of `task/<id>` into the current working branch; `scope-pr [--base B]` opens/reuses the PR from it to `main` (or `--base`), only on human request, without merging. |
| `pop_check_scope.py` | Validates committed/local/untracked diff against ownership and deny globs. |
| `pop_install_unirepo.py` | Installs/**updates** the harness declared in `_templates/unirepo-manifest.json`: mirrors the managed set into the target and writes into it the source's `content_sha` plus the **inventory** of what it wrote. The next update's prune reaches only that inventory — a managed directory is not an exclusive one, so the project's own files under `pop/scripts/` stay. `--check-fresh <dir>` recomputes it and fails closed when the target has fallen behind (`pop_validate` reports it as a violation); `--sha` prints the source's version — run from an installed copy, both report only the local version, because comparing is the installer's job; `--audit-boundary` fails a package that names anything above the target's root; `--check` only checks whether it is installed; `--audit-manifest` audits manifest closure. |
| `pop_recon.py <dir>` | Deterministic recon report of any directory (zero LLM, stdlib only): truncated tree, languages/LOC, manifests (`package.json`/`go.mod`/`pyproject.toml`/`Cargo.toml`), hotspots by git churn (degrades with a note when there is no `.git`), entry points/configs/CI and, for mostly-markdown bases, writing mode (chapters, wordcount, frontmatter). `--output [PATH]` writes to a file (default `RECON.md`) instead of stdout. |

Example:

```
python3 pop/scripts/pop_task.py my-project 1.1.1-user-table-creation --title "User table"
python3 pop/scripts/pop_task.py my-project M-1.1-adjust-contract --title "Adjust contract"
python3 pop/scripts/pop_move.py M-1.1-adjust-contract 002_planning --reason "planning started"
```

Run `python3 -m unittest discover -s pop/scripts/tests -v`, `python3 pop/scripts/pop_install_unirepo.py --audit-manifest`, and `python3 pop/scripts/pop_validate.py` before delivery.
