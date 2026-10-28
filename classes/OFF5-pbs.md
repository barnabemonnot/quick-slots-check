# OFF5: PBS relays, builders and sidecars

Cause S1. Worst seen: BREAKS, MEDIUM.

**Mechanism (CHECKED code and spec; INFERRED timing).** One-rate clocks, `G + 12*slot` checks and absolute-millisecond
timers. One relay family decides its reveal for slot `F+k` at 2k + 3 s into the slot, but the payload counts only before
`PAYLOAD_DUE_BPS` = 50 % (5.0 s at 10 s). So slot F+1 is late and from F+4 it withholds. Under ePBS the builder bids
value 0 and pays through an in-block payment, so a missing reveal leaves the proposer unpaid and the payload empty.
Pre-ePBS data put that family at 40.4-70.7 % of slots; its share after ePBS is UNVERIFIED.

**Fix (INFERRED).** Timers in basis points of `get_slot_duration_ms(slot)`. Schedule from beacon-node events.

**Wrong fixes.** Making only `current_slot()` fork-aware (no reveal from F+4). Exact fork-name gates (`== Gloas`): the
path switches off at Heze. Expecting a CL client upgrade to fix a relay.

**Find.** GEN-DURATION-12S, GEN-FORK-NAME-EQ, GEN-GENESIS-PLUS-12.

**Test.** Success and misses by slot phase with delay and load, at 10 s and separately at 8 s.

**Lead time.** One release; before the fork, after a 10 s devnet run.
