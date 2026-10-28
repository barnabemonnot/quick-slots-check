# Operator checklist

For anyone who runs or builds software that converts between slots and time. Scope: 12 s -> 10 s; 8 s is a
comparison. EIP-8198 is a candidate and is not scheduled.

Labels: checks, fixes and predicted behaviour are INFERRED. Quoted numbers come from CHECKED code reads and arithmetic.
No system has run on a real 10 s network.

For each check that applies, record the code location, owner, clock source, consumers, fix and test result. If a check
does not apply, record why. Run searches with `rg -n -e '<pattern>' <source-root>`, and also inspect imports,
configuration and callers. `python3 check/scan.py <source-root>` runs many of these searches at once.

## Core boundary test

The two-interval mapping: `t(s) = G + 12s` for `s < F`, `t(s) = T_F + d(s-F)` for `s >= F`. Inverse:
`floor((t-G)/12)` before `T_F`, `F + floor((t-T_F)/d)` after.

At `T_F` the slot must be `F`; at `T_F + d` it must be `F+1`. Check `F-1`, `F`, `F+1` and a late slot in both
directions; `T_F - 1 ms`, `T_F`, `T_F + 1 ms`; old timestamps after a restart; history after a second change. Run
`python3 -B check.py /path/adapter.py --self-test` in [vectors/](../vectors/README.md) for each real caller. A pure
function pass does not establish migration readiness.

## Start here: checks by role

| Role | Checks | Wrong fixes to refuse |
|---|---|---|
| Staking: beacon node, validator client, distributed validator, remote signer | 2, 4, 8, 13 | change `SECONDS_PER_SLOT`; set a duration override; wipe or reset slashing protection; move keys while the old signer may still run |
| L2: node, batcher, challenger, proof host | 6, 10, 13, 15 | a one-value slot-duration override; a challenger-only upgrade; a stale L1 blob schedule or prestate |
| Relay, builder, sidecar | 11, 2, 4 | fix `current_slot()` but keep millisecond timers; treat fixed latency budgets as slot fractions |
| Oracle and LST daemons | 5, 10, 4, 14 | remove a deadline gate; fix producer or consumer alone; shorten frames to keep report times |
| Light-client users, provers, relayers | 2, 7, 13 | a fork-version-only release; disable checkpoint-age or future-update checks |

**Fork-day watch list.** Duty logs for far-future or past slots; beacon-node logs of blocks from future slots; blob
requests that return 404; light-client updates rejected as future or stale; oracle reports not submitted in their
frame; relay reveals after the payload deadline; an L2 safe head that stalls. Each one points to a clock that did not
change at `F`.

## The 15 checks

1. **Find every conversion, including folded constants.** Search
   `SECONDS_PER_SLOT|SLOT_DURATION|secondsPerSlot|12000|\* *12|/ *12|12 seconds|384|1606824023|7200|2628000|2102400|blocksPer`.
   Trace each hit to a running conversion, window, rate or polling timer. Wrong fix: a literal-only replacement misses
   a folded epoch price such as `384e18/86400`. Test: boundary vectors through constructors, environment overrides,
   copied libraries and generated configuration.
2. **Name the duration source.** Search `genesis_time|GenesisTime|/config/spec|SlotDuration|slot_duration|from_spec`.
   Use a fork schedule or a slot from a verified source. Wrong fix: one API value is not a schedule; a kept 12 s value
   lags 1,440 slots per day. Test: a local file and each supported beacon API; reject missing timing data, malformed
   rows, conflicting fields and misspelled keys before defaults; accept unrelated extra fields and valid future rows.
3. **Reject "set it to 10" with the old genesis.** Search `secondsPerSlot|seconds_per_slot|slot-duration-override|genesis`.
   Keep the old interval and anchor the new one at `F`; update `d` and `G'` together. Test: with `F = 7200`, the slot
   at `T_F` is 7200; the wrong fix gives 8640.
4. **Test restart and mixed fleets.** Search `SECONDS_PER_SLOT|SLOT_DURATION_MS|cache|reconnect|restart|config/spec` in
   startup and recovery code. Wrong fix: a running process keeps 12 s while a restarted one uses 10 s from genesis; a
   30 s beacon outage can trigger this. Test: run across the fork, restart after it, disconnect the beacon source for
   at least 30 s, fail over between two sources with different legacy values.
5. **Check health and freshness gates.** Search `deadline|freshness|isHealthy|refSlot|last.*[Tt]imestamp|MAX.*AGE`.
   Compare values in the same time domain. Wrong fix: remove a deadline gate but keep the wrong data-slot mapping;
   one oracle model then repeats accounting after about 5.91 d. Test: fresh and stale input on both sides of the limit,
   before and after the fork.
6. **Use block-linked blob lookup.** Search `blob_sidecars|BlobSidecars|timestamp.*slot|slot-duration-override|parent_beacon_block_root|versioned_hash`.
   Find the beacon block that committed to this EL block, with ancestry checks, then check versioned hashes; or look up
   by versioned hash. Under ePBS, use the payload's slot number (EIP-7843) or the bid's `block_hash`; the old recipe
   "the next EL block's parent beacon root" can name a beacon block whose bid committed to other blobs. Wrong fix:
   `(timestamp-G)/10`. Test: pre- and post-fork batches with missed slots, through the node and the proof host.
7. **Use real EIP-4788 keys and bind the slot to the root.** Search `8191|BEACON_ROOTS|beaconRoots|genesis.*slot|timestamp.*12|\+ *12`.
   Take the key from a real block and prove the slot against the root. Wrong fix: a computed grid hits 1 time in 5;
   a universal `+10` fails for old history and missed slots. Test: recorded timestamps and proofs around `F`; reject
   a mismatched pair; early eviction at 16,382 s.
8. **Guard stored slot values.** Search `highest.*slot|last.*slot|slashing|attestation|checkpoint|persist`. Validate
   slots against the verified chain before a write. Wrong fix: repair the clock after a future value is stored; in one
   model, a share added or resynced while the clock is ahead is locked for 370-456 d. Never answer a lock by deleting,
   resetting or disabling slashing protection, or by moving keys while the old signer may still run. Test: a clock
   0.2F slots ahead in an isolated fixture; assert no far-future slot is persisted.
9. **Set the wall-clock intent of windows and rates.** Search `block.number|blocksPer|votingPeriod|votingDelay|endBlock|accrualBlockNumber|1 days / 12`.
   To keep seconds, multiply block windows by 1.2 and per-block rates by 5/6. Wrong fix: change clock units without
   migrating state (55-66 years of accrual at once). Test: equal seconds before and after; an open vote, open
   withdrawal, stored accrual checkpoint, compiled setter limits.
10. **Find each producer's consumers.** Search `refSlot|updatedAt|updateRate|SECONDS_PER_SLOT|WITHDRAWAL_DELAY`. Change
    both sides in one plan. Wrong fix: publish real slots to a consumer that still uses `G+12s` (stops after 5.0 d).
    Test: one report through every consumer, including queued messages and withdrawals.
11. **Check timers in milliseconds.** Search `12000|timeout|deadline|cutoff|reveal|Duration::from_millis|time.Millisecond`.
    Derive slot-phase deadlines from the active duration. Wrong fix: fix `current_slot()` but keep reveal timers
    (no reveal from F+4). Test: success and misses by slot phase, with delay and load.
12. **Measure the full governance path.** Search `FORK_EPOCH|FORK_TIME|eta|timelock|set.*Period|setInterestRateModel`.
    Do long work early; use runtime fork parameters or a fork gate for the last step. Wrong fix: wait for the final
    epoch (26-34 d) when the path takes longer. Test: rehearse with a moved fork date and a changed duration.
13. **Run the complete stack for a long interval.** Search `ForkName|fork_version|prestate|image_id|challenger|host|blob`
    in manifests. Test deployed binaries, proof hosts, prestates and contracts together: at least 1 d of 12 s history,
    then at least 7 d at 10 s, with restarts, mixed versions, blob batches, a disputed proof trace and a misnamed
    duration key. In a local devnet launcher, set the Heze slot duration explicitly; some launchers default it to
    12000 ms, which tests nothing. Seven days do not cover stops at 20-140 d; keep those UNVERIFIED.
14. **Get evidence for closed daemons.** Search available configuration and logs for `genesis|slot|epoch|SECONDS_PER_SLOT|SLOT_DURATION`.
    Require a statement of the duration source, schedule handling, restart behaviour and test results. Wrong fix:
    accept "supports the fork" with no clock evidence (a 12 s clock selects data 5 d old after 30 d).
15. **Identify the clock each L2 exposes.** Search `block.number|L1Block|l1BlockNumber|anchor`. Record the ancestor chain
    and what each counter means. Wrong fix: assume the counter is the L2 height, or switch it without migration (one
    lending simulation: borrows x4.48). Test: advance L1 and L2 independently in a model.

**CL-to-EL handoff (add to checks 1, 2, 13).** For a later EL fork or BPO at epoch `E2`, derive `T(32*E2)` from all
earlier eras (R10). Test the expected Engine API fork at the boundary, a missing block at the activation slot, and
restart on both sides.

**Your own network config.** Include the Heze duration key even when its value equals the base. With a base
`SLOT_DURATION_MS` other than the preset, a missing key makes some CL clients keep the base value while others fall
back to the preset 12000 (CHECKED in client source).

## Evidence record per check

| Field | Value |
|---|---|
| Check / owner | number 1-15; component; responsible operator |
| Applicability | applicable, or why not |
| Revision | build commit or image digest; config hash |
| Source | exact code path or document section |
| Expected | observable success, and the reference failure |
| Result | PASS / FAIL / UNVERIFIED; where the evidence is |

## Open

- UNVERIFIED: the duration, provisional and final epoch, key name, API schedule, blob values and EIP-4788 option.
- UNVERIFIED: closed-daemon behaviour and release lead times; short-reorg frequency and slot-phase margins at 10 s.
- INFERRED: keep timings distinct. Raise pure security windows early; switch rates and clocks at the fork boundary;
  run governor setters before it. Recompute the plan if fork parameters change.
