---
id: R14
title: Blob, gas-limit and base-fee rules
priority: P2
decides: ACD, with L2 teams
latest_decision: T-12 to T-9 months; under option A, final mainnet time by T-35 d
depends_on: [R8, R9]
---

# R14: blob schedule, gas-limit entry and base fee

**Gap (CHECKED).** The Heze `BLOB_SCHEDULE` row and the gas-limit entry are not decided. The base-fee rule is decided:
EIP-8198 adopted the `slot_number` rule (merged in the EIPs repository on 2026-10-23). The maximum change is
`min(slot_duration, 12)/96`, which is 5/48 at 10 s. The first block at the fork has a 12 s parent gap, so its maximum
is 1/8.

**Mechanism (CHECKED code and arithmetic).** L2 nodes and fault-proof programs compile the L1 blob base-fee fraction
and its activation time. A stale table falls back silently. The blob fee is then `p_true^(F_true/F_stale)`:

- with a scenario fraction of 12,018,519, the L1 blob fee is x1.49-1.71 and the total L1 data fee x1.21 or x1.34 on two
  measured L2s (the blob part is 29 % and 48 % of that fee);
- with a scenario fraction of 10,015,432, the L1 blob fee is x0.04-0.09 of the true cost.

Both fractions were provisional values in an earlier EIP draft and are no longer in the EIP. INFERRED: mixed node
versions can split at 10-60 s. If nodes are new and the onchain prestate is old, honest proposals cannot be defended
at the step, and withdrawals stop until a privileged role acts.

## Proposed decision (INFERRED)

- **Preferred (B):** keep `BLOB_BASE_FEE_UPDATE_FRACTION = 11,684,671` and change only target/max blobs (12/18). The
  fastest blob-fee change per second is then 2.86 % faster than today, and no L2 prestate needs new values.
- **Else (A):** final values at the mainnet fork-time decision, with about 5 weeks for L2 releases and prestate votes.
- Gas-limit entry active at least about 1 h before the fork.

**Boundary case (INFERRED).** If slot `F` is missed, the first post-fork block at `F+1` has parent `F-1` and spans
12 + 10 s over two slots, so its nominal coefficient is 11/96, not 10/96. Forecasts for the first two produced
post-fork blocks can differ from the final rule. Proposed EIP text: "Missed slots leave the ratio unchanged, and the
prediction is exact except for the second block at a new slot duration, provided that no missed slot spans the fork.
If a missed slot spans the fork, the first post-fork block uses the mean spacing of the slots it spans, and forecasts
for the first two produced post-fork blocks can differ."

## Open (UNVERIFIED)

Option A or B. A joint test of L2 nodes and prestates on a post-fork block.
