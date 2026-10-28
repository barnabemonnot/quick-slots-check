# Slot-time test vectors

These vectors test code that converts between beacon slots and wall-clock time across a slot-duration change.
EIP-8198 (Quick Slots, 12 s -> 10 s) is a candidate for the Hegotá fork. It is not scheduled. All fork epochs here
are examples, not announced dates.

Evidence labels: CHECKED = run or read; INFERRED = derived; UNVERIFIED = not checked. See [AGENTS.md](../AGENTS.md).

## Run

Python 3.10 or later. No third-party packages. No network access.

```sh
cd vectors
python3 -B check.py ref.py --self-test          # reference: exit 0
python3 -B check.py --examples --self-test      # reference passes, five wrong fixes are detected: exit 0
python3 -B check.py traps.py:constant_12        # a wrong fix: exit 1
python3 -B check.py traps.py:constant_10        # a wrong fix: exit 1
python3 -B check.py traps.py:virtual_genesis    # a wrong fix: exit 1
python3 -B minimal.py                           # optional 8-slot-epoch preset extension: exit 0
python3 -B generate.py                          # regenerate vectors.json (the checker never writes it)
```

To test your own code, write a small Python adapter that calls it, then run:

```sh
python3 -B check.py /path/to/adapter.py:my_function --self-test
```

The default function name is `evaluate`. Exit 0 = pass; 1 = at least one wrong value; 2 = the checker could not load
its inputs. A pass on pure functions is not a migration pass: run the same cases through the real callers.

## Formulas

`G = 1606824023` (mainnet genesis, Unix seconds). An epoch has 32 slots. `F` is the fork slot, `T_F` its start time,
`d` the new duration in seconds.

```text
T(s) = G + 12*s                  if s < F
T(s) = T_F + d*(s-F)             if s >= F
S(t) = (t-G) // 12               if G <= t < T_F
S(t) = F + (t-T_F) // d          if t >= T_F
epoch(s) = s // 32
epoch_start_time(e) = T(32*e)
ring_key(s) = T(s) % 8191        # EIP-4788 timestamp storage index
```

Intervals are half-open: `T(s) <= t < T(s+1)`. For more than one change, accumulate time over every earlier era.

`ref.py` integrates the schedule era by era. `generate.py` uses separate closed forms and does not import `ref.py`.

## What the vectors contain

- 22 schedules, 736 slot cases, 7,338 comparisons (CHECKED by the run above).
- First-fork epochs 451, 452 and 500000-500004 (all residues modulo 5), and 582000; each at 12 -> 10 s and 12 -> 8 s.
- Two three-era schedules (12 -> 10 -> 8 s), a fork with an unchanged 12 s duration, 10 s and 8 s from genesis, and a
  12 -> 9 s schedule at epoch 5 with the shape of a published public devnet configuration. That last case uses the
  example genesis above, not the devnet's genesis.
- Slots 0, 1, 31, 32 and these offsets from each fork: -8640, -1361, -64, -33, -32, -2, -1, 0, 1, 2, 5, 6, 31, 32,
  33, 359, 360, 7199, 7200, 8190, 8191, 8192, 8639, 8640, 8641, 10799, 10800, 10801.
- For each slot: start time, epoch, epoch start, block timestamp, EIP-4788 ring index, and inverse probes at -1 ms,
  start, +1 ms, midpoint, last millisecond and the next slot start.

Fields ending in `_ms` are Unix milliseconds; other times are Unix seconds. Schedules are `[epoch, slot_ms]` pairs.

The ring index is arithmetic only. The suite does not model missed blocks, stored roots, eviction or a contract
migration (INFERRED: each selected slot is treated as a slot with a block).

## Candidate interface

```python
def evaluate(operation, value, *, genesis_time, schedule):
    ...  # return one Python int
```

| Operation | Input | Return |
|---|---|---|
| `slot_start_ms` | slot | Unix milliseconds |
| `slot_at_time_ms` | Unix milliseconds | slot containing that time |
| `epoch_at_slot` | slot | epoch |
| `epoch_start_ms` | epoch | Unix milliseconds |
| `ring_key` | slot | timestamp index, 0-8190 |

`schedule` starts at epoch 0, strictly increases by epoch, and has positive durations. A non-`int` result fails.

## Wrong fixes the checker detects

| Name | What it does | First visible error |
|---|---|---|
| `constant_12` | keeps `G + 12*s` after the fork | `F+1` is 2 s late; 1,440 slots behind after one day at 10 s |
| `constant_10` | uses 10 s from genesis | slot at `T_F` is `1.2F`, not `F` (about one year ahead) |
| `virtual_genesis` | uses `G' = G + (12-d)*F` for all history | every pre-fork time is wrong |
| `active_from_genesis` | uses the last configured duration from genesis | as `constant_10`, also at 8 s |
| `two_eras_only` | ignores changes after the first | wrong after a second change |

A named match means the candidate gives exactly that wrong formula's results on these inputs. It does not prove how
the candidate is written.

## Input and validation contract (`--self-test`)

This is a proposed conformance contract for spec gaps R1-R3. It does not show that any client implements it.

The adapter module exports `validate_input(kind, value)` (or `evaluate.validate_input`). Expected errors are a
`ValueError` whose text is one of these codes:

| Code | Meaning |
|---|---|
| `INVALID_INPUT` | wrong type, shape, order or units |
| `PRE_GENESIS` | time before genesis; no active slot |
| `OVERFLOW` | input, product, anchor or result exceeds uint64 |
| `MISSING_KEY` | a required timing field is absent before defaults are applied |
| `CONFLICT` | parsed known timing fields disagree |
| `NON_INTEGER_TIMESTAMP` | ring request not at an integer second |
| `UNKNOWN_OPERATION` | unsupported operation or kind |

| Kind | Input and expected behaviour |
|---|---|
| `normalize_forks` | `{legacy_ms, forks: [[epoch, ms], ...]}` in consensus fork order. Last same-epoch entry wins; epoch 0 replaces row 0; far-future forks add no era; unchanged-duration rows stay. |
| `config` | raw config fields. Check `HEZE_FORK_EPOCH` and `SLOT_DURATION_MS_HEZE` before defaults. Declared aliases must agree. |
| `api` | a getSpec data object with decimal strings. Requires legacy values and a normalized schedule; allows unknown future fork names and extra fields; rejects duplicate rows. |

`--self-test` runs 48 contract cases and rejects 10 corrupt fixtures. The full cases are in `check.py`
(`contract_test`); the policy is in `conformance.py`.

## Optional preset extension

`ref.py` and `validate_input` accept `slots_per_epoch` (default 32). `minimal.py` uses it with the consensus-specs
minimal preset shape (8 slots per epoch, 6,000 ms legacy, 5,000 ms Heze; sources in `minimal-sources.json`). Genesis
0 and epochs 5 and 7 are synthetic. 408 arithmetic and 20 policy checks pass; ignoring the preset gives 191
mismatches (CHECKED by the run above).

## Open

- UNVERIFIED: final fork epoch, duration and EIP-4788 option. These vectors use examples.
- UNVERIFIED: client adapters. No client code is loaded by this suite.
- UNVERIFIED: behaviour on a 10 s network, across restarts and with missed blocks.
