---
id: R5
title: EIP-4788 eviction text
priority: P2
decides: EIP-8198 authors
latest_decision: before the first client releases
depends_on: [R4]
---

# R5: EIP-4788 eviction text

**Gap (CHECKED).** The EIP says "about a third" of old roots die "after about 4.6 hours". That is imprecise.

**Mechanism (CHECKED arithmetic).** After a 12 -> 10 s fork, post-fork timestamps overwrite ring slots that pre-fork
roots still hold.

- At most 4,095 of 8,191 pre-fork roots are evicted before 98,292 s; at most 2,730 before 81,910 s.
- The youngest evicted root is 16,382 s old: 4 h 33 m 02 s at 10 s; 32,764 s (9 h 06 m) at 8 s.
- A lookup of an evicted root reverts. It never returns a wrong root for the timestamp asked.

## Proposed text (INFERRED)

Replace the sentence with the three facts above. Keep the legacy contract; contract choices are in R4.

## Open (UNVERIFIED)

A fork-boundary test vector on a devnet with missed blocks.
