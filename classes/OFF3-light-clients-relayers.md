# OFF3: beacon light clients, provers and relayers

Cause S1. Worst seen: BREAKS, MEDIUM.

**Mechanism (CHECKED code; INFERRED timing).** As ON3, in offchain code. Light clients reject updates from `T_F + 52 s`
to `T_F + 95 s` (model estimates for fresh updates with no missed slots; a first rejection at 70.5 s was seen on a
local devnet). A relayer that waits for its clock accepts a header signed at `T_F + x` only at `T_F + 1.2x` (1.5x at
8 s).

**Fix (INFERRED).** A fork-aware clock in the same release as the fork version, used for every clock use: update
guard, checkpoint age, timeout lookup, waits (R12).

**Wrong fixes.** A fork-version-only release. A per-network constant of 10 from genesis: the guard never fires, a
1-hour-old checkpoint reads as 395 d old, and a timeout lookup fails. A re-anchor without a timed cut-over.

**Find.** GEN-DIV-12-FROM-GENESIS, GEN-SLOT-DURATION-10, GEN-SLOT-DURATION-12.

**Test.** Accept an update signed at `T_F + 60 s`; bootstrap fresh from a checkpoint just after the fork; reject a
future update.

**Lead time.** Release plus verifying key; must ship before the fork.
