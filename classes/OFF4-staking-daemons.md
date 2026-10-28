# OFF4: staking oracle daemons, provers and keepers

Cause S1/S5. Worst seen: BREAKS, MEDIUM (one case HIGH if its exposure proves large).

**Mechanism (CHECKED code; INFERRED timing).** Three patterns:

1. A gate on the 12 s grid.
2. An EIP-4788 key computed as `G + 12*slot`.
3. A scan checkpoint stored as a block number and converted back to a slot with one constant.

With an additive store, pattern 3 re-counts rewards with growth in the square of the time. In one daemon, counted/real
rewards are 12.45x at the first post-fork vote and 24x at 24 h (29x and 56x at 8 s); onchain data sizes the
share-value overstatement at most 2.7 ETH at the first vote and about 92 ETH at 72 h, if a quorum signs (INFERRED).
Stops range from 1.7 h (a key gate) to 5.07 d.

**Fix (INFERRED).** Compare like with like. Take the 4788 key from the real child block. Read the schedule at run
time, so a release can ship before the epoch is known.

**Wrong fixes.** `c = 10` after a restart. Fixing the proof anchor but not the gate. Removing a deadline gate.
Shortening report frames to keep report times.

**Find.** GEN-GENESIS-PLUS-12, GEN-4788-KEY, GEN-DIV-12-FROM-GENESIS.

**Test.** One full report cycle before and after the fork with distinct synthetic inputs; each amount counted once; a
restart after the fork.

**Lead time.** Release plus oracle members, 2-4 weeks; before the first post-fork vote.
