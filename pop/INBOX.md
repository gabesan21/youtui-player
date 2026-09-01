# INBOX

Everything waiting on a decision from you. Lists generated **automatically** by the [Dataview](https://blacksmithgu.github.io/obsidian-dataview/) plugin from the cards' frontmatter — do not edit by hand. Flow: [[WORKFLOW|WORKFLOW]].

## Awaiting your release (001)

Freshly created cards are yours to edit — the task only goes to planning once you check `- [x] Ready to plan` on the card (Release section).

```dataview
TABLE WITHOUT ID file.link AS Task, project AS Project, updated AS "Since"
WHERE stage = "001_initial_task" AND yolo != true
SORT updated ASC
```

## Awaiting plan approval (003)

```dataview
TABLE WITHOUT ID file.link AS Task, project AS Project, updated AS "Since"
WHERE stage = "003_human_approval" AND yolo != true
SORT updated ASC
```

## Awaiting merge (005_closing) — this is the verification gate outside yolo

Outside yolo there is no agentic reviewer: reviewing the PR **is** the verification. Until you merge, nothing happens — no memory, no specs, no roadmap cleanup.

```dataview
TABLE WITHOUT ID file.link AS Task, project AS Project, pr AS PR
WHERE awaiting_merge = true AND yolo != true
SORT updated ASC
```

## Blocked

```dataview
TABLE WITHOUT ID file.link AS Task, project AS Project, blocked_reason AS Reason
WHERE blocked = true
SORT updated ASC
```

## Open questions

Questions from the agent that belong to no card — decisions about the structure of the scope etc. (folder `open_questions/`).

```dataview
TABLE WITHOUT ID file.link AS Question, origin AS Origin, created AS "Since"
FROM "open_questions"
WHERE status = "open"
SORT created ASC
```

## Yolo in progress

Informational (no decision needed): tasks with gates delegated to the critic agent — see the Yolo mode section of [[WORKFLOW|WORKFLOW]]. Blocks show up under **Blocked**; the scope's delivery arrives as an open question (you test `develop` and decide whether to open the PR).

```dataview
TABLE WITHOUT ID file.link AS Task, project AS Project, stage AS Stage, updated AS "Since"
WHERE yolo = true
SORT updated ASC
```

## In progress now

Informational (no decision needed): tasks with an active agent claim — see the claim rule in [[WORKFLOW|WORKFLOW]].

```dataview
TABLE WITHOUT ID file.link AS Task, project AS Project, claimed_by AS Agent, claimed_at AS Since
WHERE claimed_by
SORT claimed_at ASC
```

## Reviews

Reports from the `weekly-review` skill are linked here, most recent first.

- [[REVIEW-2026-08-24]] — *2026-08-24: root harness review; CLAUDE.md symlink fixed, stale notes marked, 3 proposals open*.

---

Agents: nothing to maintain here beyond the **Reviews** section — the lists above derive from the frontmatter (`stage`, `critical`, `yolo`, `blocked`, `awaiting_merge` on cards; `status` on open questions) and from the release checkbox on 001 cards. To locate gates without Obsidian, run `python3 pop/scripts/pop_status.py` (grep on `stage:`/`awaiting_merge:` works as a fallback).
