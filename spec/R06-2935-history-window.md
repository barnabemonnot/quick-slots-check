---
id: R6
title: EIP-2935 history window
priority: P3
decides: EIP-8198 authors
latest_decision: when convenient
depends_on: []
---

# R6: EIP-2935 history window

**Gap (CHECKED).** EIP-8198 does not state the effect on the EIP-2935 block-hash history window.

**Mechanism (CHECKED).** The window stays 8,191 blocks. Its wall-clock length shrinks from 27.30 h to 22.75 h at 10 s
(18.20 h at 8 s). There is no early eviction. A local execution of the published history contract confirmed that
block `K` is served at `K+8191` and rejected at `K+8192`, with no extra early collision across 12 -> 10/8/9 s
fixtures.

## Proposed text (INFERRED)

Keep 8,191. State the new wall-clock length. Name EIP-7709, because a resize would also affect it.

## Open (UNVERIFIED)

No EIP-7709 or `BLOCKHASH` test was run.
