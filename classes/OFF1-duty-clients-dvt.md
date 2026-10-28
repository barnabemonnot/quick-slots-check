# OFF1: validator duty clients and distributed validators

Cause S1/S5. Worst seen: BREAKS, MEDIUM.

**Mechanism (CHECKED code; INFERRED timing).** The client reads one duration once, or has it built in, and starts the
duty for slot `F+k` at `T_F + 12k`: 2k s late (4k s at 8 s). Attestations miss from about k = 2 (20 s). In a local
devnet, one duty client's clock service matched 49/49 pre-fork samples and 2/45 post-fork samples, and its next-slot
start was late by exactly 2(s-F) seconds, reaching 180 s at F+90 (CHECKED; this ran a clock service, not duties).

**Fix (INFERRED).** Schedule from beacon-node events, or use a piecewise clock. Stop with an error if a key is missing.
Express timers in basis points of the slot.

**Wrong fixes.** A legacy-key switch plus a restart (case B in R2). Persisting far-future values: in one
distributed-validator client, a share added or resynced while the clock is ahead is locked for 370-456 d. A port that
passes one constant to a single-duration library clock (OFF6). Disabling slashing protection to get unstuck.

**Find.** GEN-SLOT-DURATION-12, GEN-GENESIS-PLUS-12, GEN-DIV-12-FROM-GENESIS, GEN-SINGLE-DURATION-API.

**Test.** Run across the fork, restart after it, disconnect the beacon source for at least 30 s, and fail over between
sources. Assert that no far-future slot is persisted.

**Lead time.** One release plus operator upgrade; a Heze release is due anyway.
