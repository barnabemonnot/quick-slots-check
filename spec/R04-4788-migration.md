---
id: R4
title: EIP-4788 migration
priority: P2
decides: ACD; EL client teams
latest_decision: T-12 to T-9 months
depends_on: [R1, R5, EIP-7843]
---

# R4: EIP-4788 migration

**Gap (CHECKED).** EIP-8198 has no text on what happens to the EIP-4788 beacon roots contract.

**Mechanism (CHECKED).** `get(ts)` returns a root only if `storage[ts % 8191] == ts`. It never returns a wrong root for
the timestamp asked; it reverts instead. A caller that computes `G + 12*m` after the fork hits a real post-fork block
1 time in 5 at 10 s (1 in 2 at 8 s) and then gets the root of a different slot than intended; otherwise it reverts.
In a 180-day sample, all high-volume callers bound the slot to the root (100 % of 130,088 calls reviewed or
bytecode-checked; CHECKED).

## Options

| Option | Meaning |
|---|---|
| (a) | No change to the 4788 contract. |
| (b) | A new slot-indexed system contract at a new address, keyed by the protocol slot number. Requires EIP-7843. |
| (c1) | New code at the 4788 address at the fork: post-fork timestamp keys go to a fresh region with a prime modulus, and the legacy ring is frozen. Needs an irregular state change. |
| (c2) | c1 plus a slot getter at the old address. |
| (d) | A new ring size for the existing ring. In place, it needs a client-level migration. |
| (e1) | Normative offchain text for `T(s)` and `S(t)` (R1). |

## Proposed decision (INFERRED)

Recommended: **(b) + (a) + (e1)**. Fallback, if ACD accepts code at the 4788 address: (c1) with a slot getter (c2).

Options c1, c2 and d change the code at the 4788 address. Proof systems that pin that code hash in their guest
programs then stop at the fork, so these options add a hard pre-fork release and image-ID deadline for them
(CHECKED mechanism). Under option (a), one proof host fails for 36.3 % of positions of a 6,000-block gap that spans the
fork (CHECKED model). A gap of at most 1,366 blocks across the fork (2,731 at 8 s) is safe.

## Open (UNVERIFIED)

The option. Image-ID and gap data from proof-system owners. A migration test.
