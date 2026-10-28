---
id: R9
title: Slot-value freeze
priority: P1
decides: ACD
latest_decision: the earlier of the first public-testnet client release and the R8 provisional epoch
depends_on: [R8]
---

# R9: slot-duration freeze

**Gap (CHECKED).** The EIP allows a fallback duration. One consensus-specs draft keeps `SLOT_DURATION_MS_HEZE: 12000` as
a placeholder; another, now closed, had 10000; the EIP's mainnet entry is 10,000 ms. No value is frozen.

**Why it matters (CHECKED arithmetic).** Fixes depend on the value: a virtual genesis is `G + 64*e_F` at 10 s and
`G + 128*e_F` at 8 s; a 6 d window of 43,200 blocks becomes 51,840 or 64,800 blocks; per-block rates scale x5/6 or x2/3; one
L2 grid of 72 s works with 8 s but not 10 s. An assumed 10 s schedule against an actual 12 s one is 1,350 epochs wrong
after 30 d.

INFERRED: in practice the value freezes at the first client release that schedules Heze on a public testnet, because
public testnets run the mainnet value. That release usually comes before T-60 d.

## Proposed rule text (INFERRED)

For ACD process and EIP-8198 Transition parameters / Fallback:

> The mainnet duration MUST be selected and frozen no later than the earlier of (a) the first client release that
> schedules Heze on a public Ethereum testnet and (b) publication of the provisional epoch under R8, and at least 60
> days before mainnet activation. Experimental devnet configurations do not freeze the mainnet duration.
> The freeze publication MUST give one exact `SLOT_DURATION_MS_HEZE` value and revision. A placeholder, range or list
> of candidates MUST NOT be labelled frozen.
> After the freeze, a different duration MUST be treated as a new transition proposal, with a new 60-day notice. This
> applies also to a return to 12000 ms. The fallback clause MUST NOT permit a late value substitution.
> Each dependent client configuration, API schedule and application parameter set MUST identify the frozen revision
> it implements.
> A change in epoch alone MUST keep the frozen duration and recalculate `FORK_SLOT` and `FORK_TIME`.

## Conditional slot-number recovery (INFERRED)

For one 12 -> d transition, a trusted post-fork block with consensus slot `s`, timestamp `t`, known genesis `G` and
frozen `d < 12` gives `F = (t - G - d*s) / (12 - d)`. Require exact division and epoch alignment. Do not substitute
the execution block number for the slot number. With an unknown duration or earlier changes, one observation is not
enough.

## Open (UNVERIFIED)

ACD must select 10000, 12000 or another tested value, and settle the R14 choices.
