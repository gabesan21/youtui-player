---
name: recon-project
description: Generates and consumes the deterministic RECON.md report (tree, languages/LOC, manifests, git hotspots, entry points/configs/CI, writing mode) of a project directory before sweeping files by hand. Use at the start of a delegated recon, in the 002 of a task that requires broad reading of the project content, and in Step 1 of import-project.
---

# recon-project

Before opening file after file to understand an unknown directory, generate a deterministic inventory with `pop/scripts/pop_recon.py` and read it first. It answers "what is in here" (tree, languages, manifests, hotspots, entry points) without spending reads on a manual sweep.

## When to generate it

- **Start of a delegated recon** (rule 18 of [[AGENTS|AGENTS]]): before launching broad-reading subagents, generate the RECON.md and pass it as context — it reduces what each subagent has to sweep on its own.
- **002_planning of a task that requires broad reading** of the project content (not just of the card): generate the report of the affected directory before deciding the plan.
- **Epoch 1 of `import-project`** (Step 1 — Codebase recon): generate the RECON.md of the imported repository/folder before launching the parallel subagents for structure, build, docs, history and fragile spots.

## How to generate it

```
python3 pop/scripts/pop_recon.py <dir>            # prints the report to stdout
python3 pop/scripts/pop_recon.py <dir> --output RECON.md   # writes to a file (default name: RECON.md)
```

Zero LLM, stdlib only, deterministic (same tree ⇒ same text). With no `.git/` in the target, the hotspots section degrades with an explicit note — the other sections stay intact. For mostly-markdown bases, the report switches to writing mode: chapter/heading structure, wordcounts and a frontmatter inventory, instead of code languages/LOC.

## How to consume it

Read the RECON.md **in full before opening any project file**. Use the sections to choose what is actually worth reading:

- **Tree** → where things are, without listing directories by hand.
- **Languages/LOC** → size and predominant stack.
- **Manifests** → declared dependencies, without opening `package.json`/`go.mod`/`pyproject.toml`/`Cargo.toml` one by one.
- **Hotspots** → which files concentrate change (git churn) — reading priority.
- **Entry points/configs/CI** → where the project starts running and how it is validated.
- **Writing mode** (markdown bases) → chapters and frontmatter before opening each note.

Only then decide which specific files to open for what the report did not answer.

## Hard rule

`RECON.md` is a **derived artifact**, regenerated on demand at any time — it is **never committed** as a source of truth, and it **never replaces** DOX, specs or memory. It guides the first reading; durable knowledge keeps living in `pop/specs/`, in the DOX contracts and in `pop/memory/`, as always.
