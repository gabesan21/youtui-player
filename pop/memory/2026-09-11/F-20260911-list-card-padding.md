---
task: F-20260911-list-card-padding
project: youtui-player
started: 2026-09-11
finished: 2026-09-11
commit: 5a2c75e
pr:
authorization: F-20260911-list-card-padding: direct-fix triage (rule 13)
---

# F-20260911-list-card-padding — taller list cards with top padding

- **Delivery:** video cards grew from 3 to 4 rows with a 1-row top padding (`SetBorderPadding`), giving thumbnails breathing room between cards in both sinks (kitty and blocks).
- **Verification:** `make build`/`make fmt`/`make vet` green; visual check assigned to the human.
- **Contract impact:** specs: none affected (visual tweak, no behavior contract) · DOX: no convention changed.

## Entries

- [[F-20260911-list-card-padding.01-card-height-padding]] — itemHeight 3→4 + 1-row top padding per card.

## Links

- **Origin:** user request after validating the kitty thumbnails — *follow for the cosmetic intent*.
