# Suggested researches — <Project name>

> Blockquotes in this template are fill-in instructions — **delete them when filling it in**.

Profile: [[pop/PROJECT|<Project name>]] · Roadmap: [[pop/ROADMAP|Roadmap]]

> **Optional** file, next to ROADMAP.md. **Deep research** prompts proposed by the agent for the **user** to run in whatever tool they prefer (deep research) and deposit the result in `pop/researches/<topic>/` (a scope whose harness lives at its own root: without the `pop/` prefix). A delivered research enriches the roadmap (epoch recon), the specs and the project itself.

## <topic-in-kebab-case>

- **Status:** pending (delivered → the section leaves the file; the synthesis is the record)
- **Feeds:** epoch <n> | spec [[pop/specs/<spec>|<spec>]] | RECON NEEDED <which>
- **Suggested prompt:**

> A complete, self-contained prompt: project context in 2–3 sentences, the central question, what the answer needs to cover (comparisons, sources, criteria) and the expected format of the result. It must work pasted into any research tool, without this repository nearby.

## How to use

1. The agent proposes researches here (`new-project`, `plan-roadmap`, `import-project`) — one section per topic.
2. The user runs the prompt wherever they want and delivers the raw result in `pop/researches/<topic>/raw/` (tip: the Obsidian Web Clipper converts web articles to markdown).
3. Result delivered → the agent runs the `ingest-research` skill: synthesis in `pop/researches/<topic>/<topic>.md`, **removal of the section from here** (the file keeps no history — the synthesis is the record) and a proposal of roadmap/spec updates (contradiction with a spec/note is flagged, never silent).
