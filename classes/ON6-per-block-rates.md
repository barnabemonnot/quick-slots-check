# ON6: per-block rates and caps

Cause S3. Worst seen: DRIFTS, LOW.

**Mechanism (CHECKED).** A per-block amount runs x1.2 per second (x1.5 at 8 s). In sampled lending markets, USD 54.1 M of
material borrows would pay about USD 0.73 M more per year (1.83 M at 8 s). Nothing reverts.

**Fix (INFERRED).** Rescale x5/6 (x2/3) at the fork with a fork-aware switch, for example an interest-rate model keyed
on `block.timestamp >= T_F`.

**Wrong fixes.** A switch from block to time accrual without migrating the stored checkpoint: 55-66 years of interest in
one accrual. Switching one market's counter on an L2 with an L1 block clock: borrows x4.48 or x13.53 at once. A plain
rate payload queued early on a timelock: anyone can execute it up to 14 d early.

**Find.** SOL-PER-BLOCK-RATE, SOL-PER-BLOCK-IDENT, SOL-BLOCKS-PER-YEAR, SOL-BLOCKS-PER-DAY, SOL-BLOCKS-PER-X.

**Test.** Accrual over equal seconds before and after the fork; continuity of balances at the switch.

**Lead time.** An interest-rate model deploy plus a proposal, 3-6 weeks; lands at `T_F` with a fork-aware payload.
