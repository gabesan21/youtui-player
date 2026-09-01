# Front <F01> — <name> — [[<id>-<slug>]]

> Blockquotes are filling instructions — **delete them when filling**.
> This file is **one executor's reading slice**: mandatory for every front that goes to a separate context, dispensable only when the task has a single front. Together with the card's What/Why and the plan's objective/strategy, it is *all* that executor receives — never the whole plan, never other fronts. Ceiling of 50 lines (validated by `pop_validate`): if it does not fit, the front is too big and splits in two.
> Do not describe code or micro-edits.

- **Delivery:** <result>.
- **Scope:** <functional boundary>.
- **Owner:** agent | user.
- **Owns:** `<files or patterns it may edit>`.
- **May read:** `<specs, contracts and areas available for consultation>`.
- **Must not edit:** `<reserved files, areas and fronts>`.
- **Depends on:** `<Fxx>` | none.
- **Expected input:** <dependency contract/artifact> | none.
- **Skills:** [[pop/skills/<skill>|<skill>]] — *use for <trigger>*.
- **Criteria:** <IDs from the [[<id>-<slug>.plan|plan]]>.

## Execution contract

- Deliver only this front's scope and criteria.
- **Know when to stop:** at most 2 attempts to make an `agent` criterion pass when the failure is environmental (sandbox, permissions, flakiness); on the second, record `ambiente`, report the reclassification to `verify: user` and move on. Never build new infrastructure just to verify.
- Missing/incompatible dependency or input → respond `BLOCKED` with evidence.
- Do not implement, simulate or repair dependencies autonomously.
- Do not edit paths outside `Owns`; return new needs to the orchestrator.

## Result

- **Status:** completed | BLOCKED.
- **Commit/artifact:** <reference>.
- **Changed files:** <short list checked against `Owns`>.
- **Divergences:** none | <divergence and orchestrator authorization>.
- **Evidence:** <relevant gate or observation>.
