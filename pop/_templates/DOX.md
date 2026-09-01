# DOX process — hierarchical agent context in the code

> PoP standard for **application** (programming) projects. **Self-contained** model, inspired by the open DOX framework (agent0ai/dox, MIT) — PoP does not depend on the original repository. Copy this entire section into the application project's AGENTS.md (it may exceed the ~150 lines to hold it); the child contracts live alongside the code.

## What it is

A tree of `AGENTS.md` files inside the code: the one at the code root is the **DOX rail** — rules for the whole project + high-level index; each relevant directory has its own, with local rules and an index of its own subtree. Each `AGENTS.md` is a **binding work contract for its subtree**: no blind edits, no stale documentation.

## Rules

1. **Before editing:** read the code's root AGENTS.md, identify **all** affected paths and **walk the tree** down to each edit location, reading every applicable AGENTS.md along the way. The walk can be delegated to a subagent that returns **only the rules applicable** to the task's paths — the executor receives the extract, not the tree.
2. **Local understanding:** any point in the code must be understandable by reading only the nearest AGENTS.md + all its parents above it. If it isn't, a contract is missing — create/complete the local one before editing.
3. **Conflicts:** the nearest document rules over local details; a child **never weakens** a parent's directive.
4. **Operational concision:** broad rules at the high levels, concrete detail in the children. Only what changes editing decisions — no prose. **Polarity:** prefer negative constraints ("never X in this subtree") and conditionals ("if Y, then Z"); avoid generic positive guidance ("follow the style") — guardrails yield +13.8pp accuracy, generic guidance −6.4pp. Cap: **~60 lines** per subtree contract; overflowed, the detail moves down into a child. Exception: a large-tree directory (many subfolders) may exceed it to hold the subtree's index — the exception covers the index, not prose.
5. **Mandatory review:** every relevant change requires reviewing the affected AGENTS.md files — update them when purpose, scope, responsibility, structure, flows, inputs, outputs or quality standards change.
6. **Closeout:** when finishing the work, re-check the changed paths, update the owning document and the affected parents, refresh the indexes, remove obsolete content and run the pertinent checks.
7. **Related contracts:** optional section in each contract with relative markdown links (`../services/payments/AGENTS.md`) to contracts of other subtrees that local decisions depend on — each link with a 1-line **trigger** (*when to follow it*). Max. **~3 laterals (ideally 0-2)** and **<7 total references** per contract (laterals + skills + children index); only a dependency that changes an editing decision (not every import); a link without a trigger doesn't count. Need more? A sign of coupling, or of routing that belongs in the parent's index. The walk becomes: vertical down to the edit location + the laterals whose trigger matches the task. The closeout (rule 6) also updates the laterals of the touched contracts. **Contract→spec link:** when the harness lives in the same repository as the code, the contract may link the theme's **spec** by relative markdown path (`pop/specs/<spec>.md`), with a trigger and counting toward the reference cap; when the harness lives outside the repository, the contract↔spec bridge is the task's card/plan — the harness does not resolve from inside the repo (the spec→contract direction always exists, in the spec template).
8. **Subtree skills:** a contract may link project skills (`pop/skills/`) **specific to that folder** — a procedure that changes how the subtree is edited (e.g. `migrations/` links the migration skill with the trigger "follow before creating/changing any migration"). Always a link with a trigger, never a copy of the content (copy = drift). **Workflow** skills (advance-task etc.) never go into a contract — they belong to the card's "Skills per stage" table: the card answers "how do I work this task"; the contract answers "what holds when editing this folder, whatever the task". Skill links count toward rule 7's reference cap.
9. **Verifiable citations:** a contract that cites a concrete file or code excerpt may pin the citation with the annotation `<!-- pop-hash: <relative-path> sha256=<hash of the cited file> -->` (HTML comment, invisible; path relative to the contract's folder; hash via `sha256sum <file>`). `pop_validate` recomputes it **fail-closed** — cited file gone or changed → violation — wherever the scope reaches the file (repos and clones present at the scope root). When revising the citation, update the hash: the violation message prints the new one.

## Initialization

Code without a DOX tree → recursive sweep and tree construction: root AGENTS.md with the general index and child contracts **only where there is an objective trigger** — do not create empty AGENTS.md files "just in case". In an imported project (`import-project`), initialization is a task of Epoch 1 (Organization).

- **Child-contract triggers:** ≥2 non-obvious conventions; a previous blind-edit error; a stack different from the rest of the repo; different ownership (another team/owner); distinct security/permission rules; legacy code.
- **The tree is born lean:** initial contracts of **20–30 lines**, growing toward the ~60 cap as real need appears; the root passed ~150 lines → move detail down into a child. Reference scale: **5–15 contracts** are enough for most repos.
- **Mandatory human curation:** the initial tree goes through gate 003 of the task that creates it — an LLM-generated contract without curation **worsens** the result (−3% success, +23% cost).

## In the PoP flow

- **002 (brief):** the planner identifies contracts applicable to likely areas and links them; broad walking happens only when a decision depends on it.
- **004:** each front walks the tree to its edit location before its first change. Reuse an extract if base/hash is unchanged; changed contracts join the delivery.
- **005:** the reviewer checks whether changes to purpose, structure, flows or rules updated contracts; no-impact changes require no rewrite.
- **A repo that must stay clean of AI files:** decide with the user in the interview — commit the DOX tree to the repo (PoP default) or keep only the root contract in the project's AGENTS.md, outside the repository.
