---
task: F-20260911-list-card-padding
entry: 02-tune-card-height
---

# Card height tuned 4→6, padding kept at 1 row

After seeing the 4-row cards, the user asked for relatively smaller padding and a taller image. Half rows are impossible in cell units, so the padding stays at the 1-row minimum and the card grew to 6 rows (5 content + 1 padding): the image nearly doubles in height (3→5 rows, ~2:1 target aspect, close to 16:9 thumbnails) and the padding share drops from 1/4 to 1/6 of the card.

## Evidence

- [[internal/ui/custom_list.go]] — *the itemHeight constant*.
