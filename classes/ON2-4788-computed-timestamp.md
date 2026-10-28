# ON2: EIP-4788 consumers that compute a timestamp

Cause S1+S4. Worst seen: BREAKS, MEDIUM.

**Mechanism (CHECKED).** `get(ts)` returns a root only if `storage[ts % 8191] == ts`. A request for `G + 12*m` after
the fork hits a real block 1 time in 5 at 10 s (1 in 2 at 8 s) and then returns the root a different block stored;
otherwise it reverts. `t + 12` never hits. Near the fork some old roots are evicted from age 16,382 s (R5). EIP-4788
itself never returns a wrong root for the timestamp asked.

Seen: a staking strategy where anyone could then mark a deposit verified with the wrong amount; an exit-delay verifier
where every exit becomes "late" after 20-25 d; an onchain randomness source known one block early; proof systems that
pin the 4788 code hash (see R4). All high-volume callers in a 180-day sample already bind slot to root (CHECKED).

**Fix (INFERRED).** Bind the slot to the root: take the key timestamp from a real block, and prove `header.slot`
against the returned root.

**Wrong fixes.** `G + 10*slot` for all history (2F seconds wrong at the fork). Removing an independent accounting or
freshness check because a comment claims a slot-age bound (accepted age can reach 9,829 slots). New code at the 4788
address, for proof systems that pin its code hash.

**Find.** SOL-4788, GEN-4788-KEY; search `8191`, `BEACON_ROOTS`, `genesis` near `slot`.

**Test.** Recorded block timestamps and matching proofs around `F`; reject a mismatched slot/root pair; test early
eviction at 16,382 s.

**Lead time.** A proof fix 3-6 weeks; a redeploy months.
