# ON4: block-count security windows

Cause S1/S2. Worst seen: BREAKS with a HIGH mechanism (in a dormant contract, so lowest priority).

**Mechanism (CHECKED code; INFERRED effect).** A window of W blocks lasts 10W s instead of 12W s, but it was sized in
wall-clock terms. This includes L2 contracts whose `block.number` is the L1 block number. A direct test of 55 L2/L3
chains found this L1 clock on 16 active chains of one rollup family and local block numbers on 26 (CHECKED).

Seen: rollup challenge periods (6.36 d -> 5.30 d), a challenge grace period with no setter, force-inclusion and
inactivity windows, restaking withdrawal delays (14 -> 11.67 d), a cross-chain gateway delay, a deposit-security pause
window (300 -> 250 s). One based rollup pins its L2 blocks to 12 s L1 slots in an immutable contract, so its node,
prover and rollup diverge from the fork. One dormant staking contract gates rewards on "due block OR due time"; at 10 s
the block gate opens first and a reward can be paid again on repeated claims.

**Fix (INFERRED).** For a wall-clock window, multiply the block count by 1.2 (1.5 at 8 s), round up, before the fork.
Raising a pure security window early is safe. Components with immutable periods need replacement.

**Wrong fixes.** Changing only the confirmation period and not the challenge period. A hard-coded `FORK_TIME` gate
voted too early. Switching an L1-number clock to timestamps without migrating stored deadlines (deadlines can expire at
once). Two time gates that were equivalent only at 12 s.

**Find.** SOL-BLOCK-WINDOW, SOL-BLOCK-DEADLINE, SOL-BLOCKS-PER-WEEK, SOL-BLOCK-TIME.

**Test.** Compare protection time in seconds before and after the change, with an open request that spans the switch.

**Lead time.** One owner call (hours) to a DAO path of 34.5-50 d. A challenge-manager replacement must be live at
least 6.4 d plus one assertion interval before the fork.
