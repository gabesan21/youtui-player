---
task: F-20260911-list-card-padding
entry: 01-card-height-padding
---

# Card height 3→4 with top padding

Each list card is now 4 rows: a 1-row top padding (`SetBorderPadding(1,0,0,0)` on the item flex — `Flex.Draw` honors `GetInnerRect`, which subtracts the padding) plus the original 3 content rows. The padding row takes the flex background, so selection/playing highlight stays continuous; the kitty placeholder's rect shifts automatically, so placements and panel clamping needed no change. Fewer items fit per page; pagination math is unchanged.

## Evidence

- [[internal/ui/custom_list.go]] — *AddItem padding and the itemHeight constant*.
