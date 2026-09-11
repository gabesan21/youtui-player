---
task: F-20260911-list-card-padding
project: youtui-player
started: 2026-09-11
finished: 2026-09-11
commit: a0a1ca6
pr:
authorization: F-20260911-list-card-padding: direct-fix triage (rule 13)
---

# F-20260911-list-card-padding — taller list cards with top padding

- **Delivery:** video cards are 6 rows: 5 content rows + 1-row top padding (`SetBorderPadding`) — taller thumbnails with breathing room between cards, in both sinks (kitty and blocks).
- **Verification:** `make build`/`make fmt`/`make vet` green; visual check assigned to the human.
- **Contract impact:** specs: none affected (visual tweak, no behavior contract) · DOX: no convention changed.

## Entries

- [[F-20260911-list-card-padding.01-card-height-padding]] — itemHeight 3→4 + 1-row top padding per card.
- [[F-20260911-list-card-padding.02-tune-card-height]] — itemHeight 4→6 after the user's visual review; padding kept at the 1-row floor.

## Links

- **Origin:** user request after validating the kitty thumbnails — *follow for the cosmetic intent*.
