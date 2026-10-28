---
id: R2
title: Beacon API slot-duration rule
priority: P1
decides: beacon-APIs authors; CL client teams
latest_decision: T-12 to T-9 months
depends_on: [R1, R3]
---

# R2: beacon API values and schedule

**Gap (CHECKED).** The beacon API has no rule for the legacy values `SECONDS_PER_SLOT` and `SLOT_DURATION_MS` across a
duration change, and no normative slot-duration schedule. `Fork{previous_version, current_version, epoch}` carries no
duration. `getSpec` is an untyped key/value dump with no required keys.

**Why it matters (CHECKED code, INFERRED effect).** No scalar value repairs a single-duration consumer: 12 is wrong
for every post-fork slot, 10 for every slot. The rule only picks how they fail.

| Post-fork `/config/spec` value | Single-value readers | Lasting damage |
|---|---|---|
| A. legacy keys stay 12; a new per-fork key is added | silent lag of k/6 slots: duties late from about 20 s; blob fetch fails at the first batch | none found |
| B. a legacy key switches to 10 | running readers keep 12; restarted readers jump 0.2F slots ahead; one validator client refuses to start | a distributed-validator slashing database locked for 370-456 d; future-epoch presigned exits |
| C. `SECONDS_PER_SLOT` removed | loud start failure in several duty clients, tools and L2 nodes | none; some readers silently use 12 or get NaN |

Keeping the legacy values fixed (A) prevents the jump. It does not repair consumers that still use one duration.

## Proposed rule text (INFERRED)

Server rules, for beacon-APIs `getSpec`:

> For the same network, `/eth/v1/config/spec` MUST keep `SLOT_DURATION_MS` and `SECONDS_PER_SLOT` at the network's
> fixed configured reference values across fork activation, node restart, reconnect and software upgrade. A duration
> fork MUST NOT change either legacy value. On mainnet these values are `"12000"` and `"12"`. They MUST NOT report
> the currently active duration. `SECONDS_PER_SLOT` MUST remain available through the Heze release series and MUST be
> derived as `SLOT_DURATION_MS / 1000`.
> The node MUST return each known `SLOT_DURATION_MS_<FORK>` together with its `<FORK>_FORK_EPOCH`. An unscheduled fork
> MUST keep `FAR_FUTURE_EPOCH` in this pair.
> The node MUST also return `SLOT_DURATION_SCHEDULE`, derived from its validated consensus configuration. It is a
> derived view, not a second consensus configuration source. The array MUST contain the effective slot-0 era and all
> configured, finite duration-fork eras, including future ones, and MUST keep historical entries after activation and
> restart. Each row MUST contain `EPOCH` and `SLOT_DURATION_MS` as decimal strings, with strictly increasing epochs
> and positive durations divisible by 1000. Start times are derived by R1 from `/eth/v1/beacon/genesis` and
> `SLOTS_PER_EPOCH`. The array MUST omit `FAR_FUTURE_EPOCH` and MUST include a scheduled duration fork even if the
> duration is unchanged. On a network with Heze at epoch 0, row 0 MUST hold the effective Heze duration; the legacy
> constants stay unchanged.

Consumer rules, for EIP-8198 Backwards Compatibility and operator guidance:

> Consumers MUST use the complete schedule, or a protocol source that supplies the slot or timestamp they need. They
> MUST NOT treat a legacy scalar as the active duration after a scheduled change.
> Before time-sensitive work, and after reconnect or a configuration update, a consumer MUST validate the schedule
> against the network identity and fork data it trusts. It MUST reject inconsistent schedules from beacon nodes for
> the same network, and MUST NOT silently replace a rejected schedule with a single-duration clock.
> If required timing data is absent, a consumer MUST refuse duties, signing, proof inputs and other work that depends
> on an unproved slot/time conversion.
> Consumers MUST tolerate unrelated extra fields and a valid later schedule row for a fork whose name they do not
> know. They MUST still reject malformed rows and conflicting known timing fields.
> Before work resumes after restart or failover, consumers MUST compare network identity and the complete normalized
> schedule. An accepted future-row update MUST be atomic.

OpenAPI fragment for `apis/config/spec.yaml` (no `required:` list, as `getSpec` has none today):

```yaml
type: object
properties:
  SLOT_DURATION_MS:
    type: string
    pattern: '^[1-9][0-9]*000$'
    description: Immutable legacy reference duration, in milliseconds.
    example: '12000'
  SECONDS_PER_SLOT:
    type: string
    pattern: '^[1-9][0-9]*$'
    description: Immutable legacy reference duration, in seconds; derived as SLOT_DURATION_MS / 1000.
    example: '12'
  SLOT_DURATION_SCHEDULE:
    type: array
    minItems: 1
    description: Effective duration eras in strictly increasing epoch order.
    items:
      type: object
      required: [EPOCH, SLOT_DURATION_MS]
      properties:
        EPOCH:
          type: string
          pattern: '^(0|[1-9][0-9]*)$'
        SLOT_DURATION_MS:
          type: string
          pattern: '^[1-9][0-9]*000$'
    example:
      - EPOCH: '0'
        SLOT_DURATION_MS: '12000'
      - EPOCH: '450000'
        SLOT_DURATION_MS: '10000'
```

Epoch 450000 is a synthetic example, not a proposed mainnet epoch.

## Alternatives (INFERRED)

(a) add duration fields to `/eth/v1/config/fork_schedule`; (b) a separate versioned schedule endpoint; (c) per-fork
keys only, which needs new key knowledge for each later fork. Switching the legacy scalar to the active value, or
removing it in Heze, is rejected: neither supplies historical eras.

## Open (UNVERIFIED)

Endpoint, field names, capitalization and the server rollout boundary. Tests of old consumers against a response with
the added array.

Test: the `api` kind in [vectors/](../vectors/README.md) (`--self-test`).
