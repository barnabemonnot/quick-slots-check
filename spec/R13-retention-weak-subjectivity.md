---
id: R13
title: Block retention and weak subjectivity
priority: P2
decides: consensus-specs authors; EIP-8198 authors
latest_decision: before the first client releases
depends_on: []
---

# R13: retention and weak subjectivity

**Gap (CHECKED arithmetic).** Block retention is 14,299 epochs. The worst-case weak-subjectivity period at 10 s is
17,108.1 epochs, so retention needs at least 17,109. The integer formula (churn term / r) gives 17,107: one epoch
short. With the default `SAFETY_DECAY = 10` the period is about 1,837 epochs, and no live-node failure was found. The
EIP also cites stale EIP numbers.

**Transition (INFERRED).** Exits and consolidations queued before the fork keep their assigned epochs. In a
stationary model at 33,554,432 ETH and `SAFETY_DECAY = 10`, the formula gives 1,830 epochs with all current limits, or
1,581 if exit and consolidation contributions stay at their old quotas while activation uses the new quota. The
249-epoch difference is 22.1 h at 10 s. This is not a cross-fork bound: queue balances, duration and state decide it.

## Proposed rule (INFERRED)

> A Heze override of `compute_min_epochs_for_block_requests()` MUST give at least 17,109 epochs (round up), or the
> spec MUST define `MIN_BLOCK_RETENTION_MS`.
> Pre-fork exit and consolidation assignments are not rescaled. Spec authors SHOULD establish conservative cross-fork
> checkpoint-freshness handling before operators rely on the current-limit value.

If EIP-8383 (fixed retention of 8,192 epochs with a configured-policy bound) is adopted, the 17,109 override is moot,
but its invariant must still be checked under the chosen Heze churn parameters.

## Open (UNVERIFIED)

A queue simulation or a cross-fork weak-subjectivity proof.
