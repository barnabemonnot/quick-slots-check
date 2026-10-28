---
id: R11
title: Engine API and simulation text
priority: P3
decides: execution-apis authors
latest_decision: when convenient
depends_on: []
---

# R11: "12 s" text in the execution APIs

**Gap (CHECKED).** The Engine API text says the slot is "12s in the Mainnet configuration". `eth_simulateV1` defaults
to a 12 s step between simulated blocks.

**Mechanism (INFERRED).** A one-block timestamp prediction from `parent + 12` is 2 s late at 10 s. Absolute Engine API
timeouts are not a slot-duration rule.

## Proposed text (INFERRED)

Fix both texts to refer to the active slot duration. Keep implementation items (parent + 12 predictions in
software, light-sync clocks, history verifiers) separate from the spec text.
