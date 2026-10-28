# Summary: getting ready for 10-second slots

EIP-8198 (Quick Slots) would shorten Ethereum slots from 12 s to 10 s. It is a candidate for the Hegotá fork
(Heze on the consensus layer, Bogota on the execution layer). It is **not scheduled**. This summary describes classes,
mechanisms and counts. Notes on specific systems go in [notes/](notes/README.md).

Evidence labels: **CHECKED** = code read, chain read, test or local devnet run; **INFERRED** = derived from CHECKED
facts; **UNVERIFIED** = not checked. No system has run on a real 10 s network, so every post-fork behaviour below is
INFERRED unless it says otherwise.

Notation: `G` = genesis time (mainnet 1606824023), `F` = fork slot, `T_F` = fork time, `d` = new slot duration,
`T-x` = x before the fork.

## The answer

Ethereum can be ready for 10 s slots with a **9-12 month plan**, if five spec gaps close early (INFERRED). No finding
is CRITICAL. One finding has a HIGH mechanism, in a dormant contract with negligible value, so it has the lowest
priority (CHECKED onchain size). Most breaks share one root cause.

## Root cause: one duration `c` in `G + c*slot`

Code converts between slot and time with one duration: `T = G + c*slot` or `slot = (t - G) / c`. **No single `c` is
right on both sides of the fork** (CHECKED arithmetic):

- `c = 12` lags the real slot by Δ/60 slots, Δ seconds after the fork: **1,440 slots per day**. Data that a 12 s grid
  selects τ after the fork is τ/6 old.
- `c = 10` from genesis runs **0.2F slots ahead** at the fork (2F seconds): about one year for a fork in 2027-2028.

This holds in code for every open-source offchain system rated BREAKS with a clock pattern (CHECKED). For
closed-source daemons it is INFERRED.

## The fix: a piecewise schedule

Use an accumulated per-era schedule, or read the slot from its source.

```text
T(s) = G + 12*s           for s <  F        S(t) = (t - G) // 12          for t <  T_F
T(s) = T_F + d*(s - F)    for s >= F        S(t) = F + (t - T_F) // d     for t >= T_F
```

- Each era has an anchor `(FORK_SLOT, FORK_TIME, duration)`. For more than one change, accumulate time over every
  earlier era.
- Or take the slot from a source: the EIP-7843 slot number, the block root, beacon-node events, or the real execution
  block timestamp.
- A "virtual genesis" `G' = G + (12 - d)*F` is only a shortcut inside one era. It is wrong for pre-fork times, wrong
  after a second change, and wrong if `d` changes without `G'`. See [spec/R01](spec/R01-slot-time-formula.md).

[vectors/](vectors/README.md) tests any implementation of this rule. `python3 check/scan.py <path>` finds candidate
code (see [AGENTS.md](AGENTS.md)).

## The most common wrong fix

**"Set the constant to 10 and keep the genesis."** It was seen in 10 or more offchain systems (CHECKED code). The
clock then runs about a year ahead. In one staking oracle class, one report could then add 9.9-17.3 % of the pool's
value (INFERRED). Other wrong fixes recur: a release that adds only the new fork version, a library bump that keeps a
single-duration API, a partial fix of a shared clock, a one-value override flag, a clock switch without a state
migration, a fix at the wrong time, and a fix of one side of a producer/consumer pair. The full list is in
[checklists/wrong-fixes.md](checklists/wrong-fixes.md).

## The beacon API value decides how unfixed software fails

Every consensus client serves `SECONDS_PER_SLOT = 12` and `SLOT_DURATION_MS = 12000` on mainnet today (CHECKED, six
client source trees). Four have unreleased Heze code that keeps these legacy values and adds a per-fork key. None has
released it (CHECKED). If the legacy keys stay at 12, single-value readers lag slowly and write no lasting bad state.
If a legacy key switches to 10, restarted readers jump about a year ahead. One distributed-validator node class then
locks each share it touches for 370-456 days (INFERRED from CHECKED code). No spec text says this today: spec gaps R2
and R3.

## What breaks first, if nobody acts

CHECKED code; INFERRED timing.

| After the fork | Class |
|---|---|
| 20-60 s | validator duty clients and distributed validators miss duties |
| slot F+1 | relays and builders miss the payload deadline |
| 52-95 s | light clients reject fresh updates (model estimates; a first rejection at 70.5 s was seen on a local devnet, CHECKED) |
| first post-fork blob batch | L2 nodes and proof hosts ask for the wrong slot's blobs and stop (one node class after about 2-3 min) |
| about 74 min | a bridge relayer's fresh-header waits can time out (conditional on snapshot age and polling) |
| 1.7-5.7 h | a validator key gate in a staking daemon |
| 4.76-5.00 h | a beacon light client on another chain underflows onchain |
| 16.5 h to about 5 d | staking oracle daemons stop at their deadline gates |
| 3.5-7 d after a dispute starts | a rollup fault-proof game, if an old proof host is still in use |

## The most serious findings, as classes

- **An LST oracle daemon can sign an inflated value** (MEDIUM; HIGH if its exposure proves large). It re-counts a
  reward after the fork (CHECKED code; re-count CHECKED on a local devnet; signing effect INFERRED). A release before
  the fork fixes it.
- **L2 security through offchain software** (MEDIUM). A rollup's permissionless fault-proof game depends on offchain
  programs. An old version of one fails only during a dispute (INFERRED from CHECKED code).
- **Staking oracle clocks onchain** (MEDIUM). Reports of three staking systems stop at a predictable time (CHECKED
  mechanism, INFERRED timing).
- **Some block-counted parameters have no setter** (CHECKED mechanism). Keeping their wall-clock length then needs a
  logic upgrade. Check every block-counted parameter for a setter.

Ratings follow [RATING.md](RATING.md). A blind re-rating by a second model family kept 37 of 46 MEDIUM+ ratings and
proposed five one level lower. None rose. Reach is unmeasured for most MEDIUM+ notes.

## Spec gaps

Every row is a gap: the EIP or the specs do not say it today (CHECKED). Each recommendation is INFERRED.

| ID | Gap | Priority |
|---|---|---|
| [R1](spec/R01-slot-time-formula.md) | no normative slot<->time formula across the fork | P1 |
| [R2](spec/R02-beacon-api-schedule.md) | no beacon API rule for legacy values and the schedule | P1 |
| [R3](spec/R03-stable-duration-key.md) | no stable key name; missing keys fall back silently | P1 |
| [R4](spec/R04-4788-migration.md) | no EIP-4788 migration text | P2 |
| [R5](spec/R05-4788-eviction-text.md) | EIP-4788 eviction text is imprecise | P2 |
| [R6](spec/R06-2935-history-window.md) | EIP-2935 window change not stated | P3 |
| [R7](spec/R07-request-fee-dynamics.md) | EIP-7002/7251 fee dynamics not stated | P3 |
| [R8](spec/R08-provisional-fork-epoch.md) | the final fork epoch comes too late for long paths | P1 |
| [R9](spec/R09-freeze-slot-value.md) | the slot value is not frozen | P1 |
| [R10](spec/R10-el-fork-bpo-time.md) | later EL fork and BPO times | P2 |
| [R11](spec/R11-engine-api-simulate-text.md) | "12 s" text in the execution APIs | P3 |
| [R12](spec/R12-light-client-duty-clock.md) | light-client and duty clock rule removed | P2 |
| [R13](spec/R13-retention-weak-subjectivity.md) | block retention below worst-case weak subjectivity | P2 |
| [R14](spec/R14-blob-gas-base-fee.md) | blob schedule and gas-limit entries | P2 |

## Decisions and timeline

INFERRED plan; history rows CHECKED.

| When | Action |
|---|---|
| T-12 to T-9 months | Adopt R1 and R2. Select the R3 key name. Decide R14 (blob values) and R4 (4788 option). Publish the class checklist, wrong-fix list and test vectors. |
| T-12 to T-6 months | Engage every owner of a priority-1 finding. Start with fixes that need no fork parameter or need a migration. |
| T-6 months | A 10 s devnet with the operator stack and at least one day of 12 s history. |
| T-3 to T-2 months | Public testnets at 10 s, run for at least 7 days (history: 36-72 d before mainnet). |
| first public-testnet release, or T-60 d at the latest | Freeze the slot value (R9) and the key name (R3). Publish a provisional fork epoch (R8). |
| T-35 d | Final mainnet fork time, if blob values must be compiled into L2 proof artifacts. |
| T-34 d | Historical final epoch (26-34 d before the fork in six forks). Client releases at 15-33 d. |
| T_F to T_F + 30 d | Monitor 4788 reverts, oracle cadence, L2 derivation lag and light-client head age. |

Why the dates matter: the longest governance paths are 42-57 d (CHECKED history and onchain minimums), fault-proof
prestates about 5 weeks, redeployments months. Owners who need the fork time or slot value as a constant cannot start
until these are fixed. Designs that read fork parameters at run time can ship early.

## What this research does not cover

- **No real 10 s network.** Post-fork behaviour comes from code, models and short local devnets.
- **Onchain coverage is partial.** The systems in our notes hold 29.4 % of the onchain value in the census union
  (98.1 % with two large contracts that were checked and found unaffected). Held value undercounts systems whose value
  sits elsewhere. All EIP-4788 call volume in a 180-day window was reviewed.
- **Bytecode coverage.** A census covered 7,898,620 verified mainnet addresses and 984,957 distinct runtimes. It does
  not see storage values, calldata values, unverified code or offchain code.
- **Offchain coverage came from class lists, not a population.** 27 census reports, about 300 components, 97
  findings. About 40 closed-source systems could not be searched.
- **Not covered at all:** custodians and exchanges as operators, institutional staking tooling, most wallets,
  restaking-service software, searchers, the long tail of library dependents, L2-only and non-mainnet deployments, and
  code written after the census.
- **Error rates.** Half of the top 60 text-census hits were code that does not run. 7 of 20 top "BREAKS" calls were
  refuted on review. A pattern hit is a lead, not a finding.

## Main uncertainties

1. Two consensus clients have not stated a duration policy (UNVERIFIED).
2. One relay family's share of blocks after ePBS (Gloas) is unknown. It decides one priority (UNVERIFIED).
3. The short-reorg rate at 10 s, which some bridges depend on (needs a devnet).
4. The final key name, slot value, blob values and 4788 option.
5. Impact ratings say little about scale. Reach is unmeasured for most notes.
