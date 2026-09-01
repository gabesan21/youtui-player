---
name: update-harness
description: Checks whether this repository's harness is up to date with the original PoP (https://github.com/gabesan21/project-of-projects) and updates it respecting the format — git merge for a full fork, managed reinstall for an included repo. Use when the user asks to update the harness, sync with the original PoP or check whether the workflow fell behind.
---

# update-harness

Keeps this repository's harness current with the original PoP **without trampling what belongs to the user**. Upstream changes are always *merged* into the local state — never blindly overwritten.

**Always runs outside the kanban.** Harness updates are maintenance of the material the kanban consults — no card, branch, worktree or task PR (rule 13 and "Current scope" in [[WORKFLOW|WORKFLOW]]).

## Principles

- **Confirmation before writing:** the skill checks and proposes; the human confirms before any merge or reinstall. Push, never — only on explicit order.
- **Nothing is lost:** a fork updates through git merge (a conflict becomes the human's decision); an included repo updates through the managed reinstall, which only overwrites the managed set and only prunes what the previous inventory recorded. Specs, roadmap, memory, notes and the user's own files stay intact by construction.
- **A managed file edited locally is drift:** if `git status` shows local modifications inside the managed set, report them to the human before updating — the update discards them by design, but never silently.

## 1. Detect the format

- `pop/.unirepo-harness.json` exists → **included** (harness installed by `pop_install_unirepo.py`).
- No marker and the root has `WORKFLOW.md` + `kanban/` → **fork** (a full copy of the PoP).
  - If the `origin` remote already is `https://github.com/gabesan21/project-of-projects`, this repo is a **clone of the source**: update with a plain `git pull` and stop.
- Neither → this repo does not use the PoP; say so and stop.

## 2. Check freshness

### Included

The marker stamps the `content_sha` of the harness at the source at install time.

1. Find the source — **ask the human if unknown**: a local PoP checkout (the one that installed this repo) or the public repository. With no known local source, make a shallow clone of the public repo into a temporary folder: `git clone --depth 1 https://github.com/gabesan21/project-of-projects /tmp/pop-upstream`.
2. Compare: `python3 <source>/pop/scripts/pop_install_unirepo.py --sha` against the `content_sha` field in `pop/.unirepo-harness.json`. Equal → harness is current, stop.
3. **Different-source warning:** a different sha can mean the harness fell behind *or* that the source differs from the one that installed it (another language, another version). Reinstalling from the public repository over a harness installed from a source in another language **switches the language of the entire harness**. In that case, stop and confirm with the human before proceeding.

### Fork

1. `git remote add upstream https://github.com/gabesan21/project-of-projects` (if absent) and `git fetch upstream`.
2. `git log --oneline HEAD..upstream/main` empty → current, stop. Otherwise, list the new commits for the human.

## 3. Update (after confirmation)

### Included → managed reinstall

1. Is `git status` clean on managed files? If any of them carry local edits, show the `git diff --stat` before proceeding.
2. `python3 <source>/pop/scripts/pop_install_unirepo.py .` — idempotent: overwrites only the managed set and prunes only what the previous inventory authorizes.
3. Dedicated commit in the repo: a short message stating the harness was updated (e.g. `chore: update PoP harness`).

### Fork → git merge

1. `git merge upstream/main` on the fork's default branch. Never `reset --hard`, never automatic `--ours`/`--theirs`.
2. Upstream only carries harness — your own content (projects, notes, memory) does not exist there, so the merge does not touch it.
3. Conflict → stop and present the conflicting files to the human; the decision is theirs.

## 4. Report

Close with a short summary: detected format, previous version → current version (sha or commit range), managed files touched and any drift discarded with the human's knowledge.
