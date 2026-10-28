# OFF2: L2 nodes, proof hosts and L2 consensus inputs

Cause S1/S6. Worst seen: BREAKS, MEDIUM.

**Mechanism (CHECKED code; INFERRED for full stacks).** The node asks the beacon node for blobs at slot `(t - G)/c`.
For the L1 block at slot `F+k` this gives `F + floor(10k/12)`, correct only for k = 0. Derivation stops at the first
post-fork blob batch, and proof hosts share the bug. In local devnets, two fetch paths succeeded on all pre-fork
samples and failed on all post-fork samples, from F+1 (CHECKED for the fetch path only).

A second input: L2 nodes and fault-proof prestates compile the L1 blob base-fee fraction (R14). A stale table changes
the L1 blob fee silently. If nodes are new and the onchain prestate is old, honest proposals cannot be defended at the
step, and withdrawals stop until a privileged role acts. An old proof host fails only during a dispute; the loss would
come 3.5-7 d after game creation.

**Fix (INFERRED).** Find blobs by the beacon block that committed to this EL block, by versioned hash, or by the
EIP-7843 slot number. Under ePBS, the old recipe "the next EL block's parent beacon root" can name a beacon block whose
bid committed to other blobs. Keep the blob fraction unchanged at Heze if possible. Readiness test: a host trace on a
post-fork block.

**Wrong fixes.** A one-value `slot-duration-override` flag (every blob request returns 404). Upgrading the challenger
alone. A fork name in the wrong case in config. Rescaling the L2 sequencing window.

**Find.** GEN-DIV-12-FROM-GENESIS, GEN-OVERRIDE-FLAG, GEN-SLOT-DURATION-10; search `blob_sidecars`,
`parent_beacon_block_root`.

**Test.** Fetch blobs for pre- and post-fork batches, with missed slots, through both the node and the proof host.

**Lead time.** Node release before the fork; prestate vote about 28-35 d (option A of R14), nothing under option B.
