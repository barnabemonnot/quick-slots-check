# ON8: paired constants

Cause S1/S2. Worst seen: BREAKS (only after a one-sided fix), MEDIUM.

**Mechanism (CHECKED code; INFERRED effect).** Two contracts, or a contract and a daemon, share a 12 s or block-count
assumption. A fix of one side breaks the pair. If a staking oracle moves its reference slot to real slots, its L2 rate
pushers that still use `G + 12*s` run ahead by τ/5, and L2 rate updates revert after 5.0 d (2.0 d at 8 s). If a
restaking layer raises its withdrawal delay while a dependent contract keeps the old mirror value, a convenience call
reverts on a newly premature completion.

**Fix (INFERRED).** Find every consumer of a 12 s producer first. Move both sides in one action.

**Wrong fixes.** The producer fix alone. The consumer fix alone. An offchain model fix without the contract.

**Find.** Search the producer's outputs (`refSlot`, `updatedAt`, delay constants) across contracts, bridges, adapters
and daemons.

**Test.** Follow one report through every consumer before and after the change, including queued cross-chain messages
and withdrawal requests made before the change. Check day 6.

**Lead time.** The same governance action as the producer fix.
