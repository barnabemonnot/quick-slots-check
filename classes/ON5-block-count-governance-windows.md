# ON5: block-count governance windows

Cause S2. Worst seen: DRIFTS, LOW (one with high priority because it has no setter).

**Mechanism (CHECKED).** Voting windows in blocks last x5/6 (x2/3 at 8 s). 1,972 of 2,252 live governors (88 %) use a
block clock. Compiled setter bounds keep their old meaning (5,760 blocks = 16.0 h). No governor stops.

**Fix (INFERRED).** x1.2 through the setter, executed 3.25-5.25 d before the fork (worst error 7.1-7.8 %, against
-16.7 % unfixed), because each proposal copies its parameters at creation. A governor with no setter needs a new
governor (1-3 months).

**Wrong fixes.** Switching to a timestamp clock while a proposal is open (in an EVM test an Active proposal became
Succeeded at once). Running the setter at or after the fork. Declaring all bounded setters unusable: all 58 bounded
sample rows accept x1.2.

**Find.** SOL-GOV-BLOCKS; search `votingPeriod`, `votingDelay`, `clock(`, `CLOCK_MODE`.

**Test.** Proposals created before and after the setter; vote-state continuity across a clock change.

**Lead time.** Forum post at about T-5 weeks; proposal created at about T-14 d; setter executes T-5.25 to T-3.25 d.
