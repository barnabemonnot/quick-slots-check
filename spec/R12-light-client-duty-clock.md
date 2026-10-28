---
id: R12
title: Light-client and duty clock
priority: P2
decides: consensus-specs authors
latest_decision: before the first client releases
depends_on: [R1]
---

# R12: light-client and duty clock rule

**Gap (CHECKED).** One consensus-specs draft deletes the MUST that tied the light-client `current_slot` and duty
schedulers to the fork-aware clock, and has no Heze light-client file. The CL helpers themselves are correct.

**Mechanism (INFERRED from CHECKED code).** A light client asserts `current_slot >= update.signature_slot` with a local
clock. A `(now - G)/12` clock falls behind after the fork and rejects fresh updates from about 52-95 s. A relayer that
waits for its clock accepts a header signed at `T_F + x` only at `T_F + 1.2x`.

## Proposed rule (INFERRED)

> Light clients and duty schedulers MUST compute the current slot with the accumulated schedule (R1).
> Light-client configuration MUST include every `SLOT_DURATION_MS_<FORK>` with its epoch.
> One function MUST serve every light-client and relayer clock use: the update guard, checkpoint age, timeout lookup
> and waits.

## Open (UNVERIFIED)

A Heze light-client spec file; a fork-boundary test vector for update acceptance at `T_F + 60 s`.
