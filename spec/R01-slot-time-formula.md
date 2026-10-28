---
id: R1
title: Normative slot-time formula
priority: P1
decides: EIP-8198 authors; consensus-specs authors
latest_decision: T-12 to T-9 months
depends_on: [R4, EIP-7843]
---

# R1: slot and time conversion

**Gap (CHECKED).** EIP-8198 has no closed form for slot<->time across the fork, no named fork anchors
(`FORK_SLOT`, `FORK_TIME`), no rule that `genesis_time` stays the time of slot 0, and no limits on a "virtual genesis".

**Why it matters.** Most breaks found share one cause: code that uses one duration `c` in `G + c*slot`. No single `c`
is right on both sides of the fork. See [SUMMARY.md](../SUMMARY.md).

## Closed form (CHECKED arithmetic)

Mainnet, one change from 12 s to `d` s at slot `F = 32*e_F`, `T_F = G + 12*F`:

```text
T(s) = G + 12*s                 if 0 <= s < F
T(s) = T_F + d*(s - F)          if s >= F
S(t) = (t - G) // 12            if G <= t < T_F
S(t) = F + (t - T_F) // d       if t >= T_F
T(F) = T_F; S(T_F) = F
T(S(t)) <= t < T(S(t) + 1)      for t >= G
```

## Proposed rule text (INFERRED)

For EIP-8198, Parameters / Slot duration schedule:

> `HEZE_FORK_EPOCH` names this transition's activation epoch. `SLOT_DURATION_MS_HEZE` gives the duration from that
> epoch. `SLOT_DURATION_MS` remains a fixed network configuration reference; it MUST NOT change or be removed on that
> network after genesis. This field policy does not select the denominator for reward, inactivity-penalty or churn
> scaling.
> Timing helpers MUST derive the effective era sequence from the per-fork configuration.

For EIP-8198, Wall-clock timeline; mirror in consensus-specs timing helpers:

> `genesis_time` MUST remain the Unix time of slot 0. A fork MUST NOT change this value in beacon state or in
> `/eth/v1/beacon/genesis`.
> Let `G = genesis_time`, `E = HEZE_FORK_EPOCH`, `N = SLOTS_PER_EPOCH`, `FORK_SLOT = E * N`, and
> `d = SLOT_DURATION_MS_HEZE / 1000`. For a network with 12-second slots before this fork and no earlier duration
> change, `FORK_TIME = G + 12 * FORK_SLOT`.
> `FORK_SLOT` is the first slot with duration `d`. Its start time is `FORK_TIME`, whether or not that slot has a block.
> CL clocks, fork-choice clocks, duty clocks, light clients, EL-side applications, L2 proof hosts and configuration
> generators MUST use the accumulated schedule for their slot/time conversions.
> Slot duration MUST be positive and an integer number of seconds. Implementations MUST keep millisecond precision for
> intra-slot deadlines.
> Intra-slot callers MUST compute `time_into_slot = time_ms - T_ms(slot)`. They MUST NOT use a modulus with the
> active duration. Each phase deadline MUST use the deadline rule of the fork of the slot being timed.
> Times before `genesis_time` have no containing slot. A caller MUST reject them or handle them before it calls the
> helper. It MUST NOT let unsigned subtraction wrap.
> For more than one duration change, implementations MUST accumulate time over all earlier eras. They MUST NOT use
> `G + duration * slot` over eras with different durations.
> The schedule MUST start at slot 0, have strictly increasing start slots, and activate each later era at its
> network upgrade epoch. Forks at the same epoch MUST resolve in consensus fork order. An unscheduled fork at
> `FAR_FUTURE_EPOCH` MUST NOT create an era. A fork at epoch 0 MUST set the duration of the slot-0 era.
> `FORK_TIME` for any later fork MUST be the time of its start slot on the accumulated schedule.
> Arithmetic MUST be exact. Implementations with bounded integers MUST reject overflow.

Pseudocode (`eras` is the validated, normalized list of `(start_slot, duration_ms)`):

```python
def compute_time_at_slot_ms(genesis_time_ms, slot, eras):
    assert slot >= 0 and eras[0][0] == 0
    start_time = genesis_time_ms
    for i, (start_slot, duration_ms) in enumerate(eras):
        next_slot = eras[i + 1][0] if i + 1 < len(eras) else None
        if next_slot is None or slot < next_slot:
            return start_time + (slot - start_slot) * duration_ms
        start_time += (next_slot - start_slot) * duration_ms

def compute_slot_at_time_ms(genesis_time_ms, time_ms, eras):
    assert time_ms >= genesis_time_ms and eras[0][0] == 0
    start_time = genesis_time_ms
    for i, (start_slot, duration_ms) in enumerate(eras):
        next_slot = eras[i + 1][0] if i + 1 < len(eras) else None
        if next_slot is None:
            return start_slot + (time_ms - start_time) // duration_ms
        next_time = start_time + (next_slot - start_slot) * duration_ms
        if time_ms < next_time:
            return start_slot + (time_ms - start_time) // duration_ms
        start_time = next_time
```

Worked example: `G = 0`, `N = 32`, 12 -> 10 at epoch 451, 10 -> 8 at epoch 457.

| Boundary | Slot | Start (s) |
|---|---|---|
| first change, 12 -> 10 | 14432 | 173184 |
| next slot | 14433 | 173194 |
| second change, 10 -> 8 | 14624 | 175104 |
| next slot | 14625 | 175112 |
| a later EL fork at epoch 458 | 14656 | 175360 |

### Virtual genesis rule (for Backwards Compatibility)

> The normative object is the era sequence. Each era is anchored by `(FORK_SLOT, FORK_TIME, d)`. Implementations
> SHOULD store and compare these anchors, not a derived offset.
> An application MAY use a local offset `G_virtual = FORK_TIME - d * FORK_SLOT` for the new era. With a 12-second
> first era and 32 slots per epoch this is `G + 64 * E` at 10 seconds and `G + 128 * E` at 8 seconds. It is not a
> genesis time. This shortcut MUST satisfy all four conditions:
> 1. It MUST convert only slots at or after `FORK_SLOT` and times at or after `FORK_TIME`.
> 2. It MUST stop at the next duration change.
> 3. The offset and duration MUST change atomically.
> 4. The offset MUST be separate from the network genesis time and MUST NOT replace a genesis value used for identity
>    checks, proofs or pre-fork history.
> A light client that verifies history across the fork MUST use the full schedule for that history.
> A contract SHOULD use the protocol slot number (EIP-7843) where it is active. A contract MUST NOT equate execution
> block number with beacon slot number.

## Alternatives (INFERRED)

(a) the full schedule everywhere (preferred); (b) a local virtual offset for one era, under the four limits; (c) an
authenticated slot or timestamp from the protocol. A new EL schedule contract adds another configuration source and
is not needed.

## Open (UNVERIFIED)

- Spec authors must choose the economic ratio base. One consensus-specs draft scales rewards, inactivity and churn
  against the configured `SLOT_DURATION_MS`; the EIP uses the effective duration at `GENESIS_EPOCH`. They differ on a
  network that activates Heze at epoch 0.
- Add `assert time_ms >= genesis_time_ms` to the consensus-specs `compute_slot_at_time_ms`.
- Confirm same-epoch fork order in the final spec.

Test: [vectors/](../vectors/README.md).
