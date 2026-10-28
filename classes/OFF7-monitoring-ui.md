# OFF7: monitoring, explorers, indexers and UIs

Cause S1. LOW by default; one MEDIUM case.

**Mechanism (CHECKED code).** 384 s epochs, 7,200 slots per day, 12 s countdowns. No indexer we found feeds an onchain
decision. Cases: a liquidation-runway display that uses a fixed blocks-per-day constant shows a runway x1.21 too long (x1.51),
so owners can fall below a threshold (DRIFTS, MEDIUM); an API health check first fails at 25 min; an explorer loses
blobs after 91 d; a countdown to a block 50,400 ahead is 28 h too long.

**Fix (INFERRED).** Take slot and epoch times from the beacon API schedule, the piecewise formula, or the real block
timestamp. Label UI times as estimates and label "epoch" durations by fork.

**Wrong fixes.** A display constant of 10 from genesis (dates about one year wrong). A per-day constant fix that does
not follow the frozen slot value (R9).

**Find.** GEN-EPOCH-384, GEN-SLOTS-PER-DAY-7200, SOL-BLOCKS-PER-DAY.

**Test.** Display values for a date 30 d after the fork against the piecewise formula.
