---
id: R10
title: EL fork and BPO activation time
priority: P2
decides: EL configuration authors; EIP-7892
latest_decision: before the first client releases
depends_on: [R1]
---

# R10: EL fork and BPO times after the fork

**Gap (CHECKED).** No rule says how to compute the timestamp of a later EL fork or blob-parameter-only (BPO) fork at
epoch `E2` after a duration change.

**Mechanism.** `G + 384*E2` is late by 64 s per post-fork epoch at 10 s (128 s at 8 s) (CHECKED arithmetic). INFERRED:
a wrong timestamp makes every EL client return Engine API error -38005 "Unsupported fork", and the chain stops;
different values across clients can split it.

## Proposed rule (INFERRED)

> The activation timestamp of an EL fork or BPO at epoch `E2` MUST be
> `compute_time_at_slot(compute_start_slot_at_epoch(E2))` on the accumulated schedule (R1), not `G + 384*E2`.
> EL consensus need not load a CL schedule to use an already derived timestamp.

Optional: a startup cross-check through `eth_config`.

## Open (UNVERIFIED)

Client implementation; a boundary test with a missing block at the activation slot.
