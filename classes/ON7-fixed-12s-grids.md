# ON7: fixed 12 s grids and folded constants

Cause S1+S5. Worst seen: BREAKS, MEDIUM.

**Mechanism (CHECKED).** A system builds its own grid on 12 s L1 slots. One L2 has 72 s slots; 72/10 = 7.2, so 1
proposal in 5 lands in the previous L2 slot and reverts (2 in 5 with pipelining). At 8 s with a matching epoch, every
proposal of one version reverts. A folded constant can hide the 12: one contract charges epochs at
`384e18 / 86400 = 4444444444444445` per epoch, which no text scan for "12" sees.

**Fix (INFERRED).** Use real L1 block times, or grid lengths that divide every candidate slot time (120 s). Change a
folded constant and its offchain model together.

**Wrong fixes.** Setting the node's duration to 10 alone (the node rejects `72 % 10 != 0`, so it needs a coordinated
release). A one-sided fix of the folded constant (see ON8).

**Find.** SOL-TWELVE-ARITH, SOL-FOLDED-EPOCH-PRICE.

**Test.** Every boundary phase at 10 s and separately at 8 s; the same charge for the same elapsed time on both sides.

**Lead time.** A coordinated release plus new-rollup governance (about 13 d).
