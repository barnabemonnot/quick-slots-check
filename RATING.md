# Rating rubric

How to rate the impact of one system's incompatibility with 10 s slots. Status: proposal. EIP-8198 is a candidate and
is not scheduled.

Each note has three separate fields:

- **Effect:** BREAKS (stops or gives wrong results), DRIFTS (correct, but the wall-clock meaning changes), BENIGN.
- **Impact:** HIGH, MEDIUM, LOW, NONE (this rubric).
- **Priority:** how early the owner needs to know. **P1** = engage at T-12 to T-6 months: a core function with material
  value stops or goes wrong at or soon after the fork, no fix is possible after the fork, or the fix needs a
  governance path that must start before the fork. **P2** = by the public 10 s testnet (about T-3 months). **P3** =
  checklist only. A long governance path raises priority, not impact.

## 1. Principles

1. **Impact is the change to the system's function after a fork to 10 s, if nobody acts.** It is not how clever the
   mechanism is, how surprising the result is, or how large the protocol is.
2. **Rate the four axes one at a time, then read the level from the table in section 3.** A rating that departs from
   the table says why in one line.
3. **Rate the live binding at a pinned block:** the proxy and its current implementation, the current parameters, and
   the release that operators run. Do not rate a worst-case setting the system does not use.
4. **Missing evidence never raises a level.** An unmeasured reach is R1. When in doubt, take the lower level and record
   the higher one as a paired verdict ("MEDIUM; HIGH if <condition>").
5. **The author proposes; a triager rates.** A triager from another model family, or a human, rates blind (section 5).

## 2. Axes

| Axis | Level | Definition |
|---|---|---|
| Impact | I4 | Permanent loss: funds, a right or a function are lost, and no party can restore them after the fork (immutable code, consumed state, a signed result that cannot be undone). |
| Impact | I3 | Value or a right is lost or held until a privileged party acts: an upgrade, governance, a slashing appeal, a manual rescue. Users cannot recover alone. |
| Impact | I2 | A function stops or gives wrong results until the team ships a change (release, parameter, upgrade). No value is lost if the team acts. Also: a safety window (fraud proof, challenge, confirmation) shorter than its design sizing. |
| Impact | I1 | A small or slow change: a rate, window or schedule that drifts by 1/6, with no safety role; a delay that ordinary retry or the next release fixes. |
| Impact | I0 | No change in function (cosmetic, logs, display, gas cost). |
| Trigger | T3 | Certain at the fork in the default setting: the path runs every slot, epoch or report. |
| Trigger | T2 | Happens in normal use after the fork (a lock or vote that spans the fork, the next batch), or any unprivileged party can cause it at small cost. |
| Trigger | T1 | Needs an unusual but plausible setting, a rare path, or a specific timing. |
| Trigger | T0 | Only constructed: no live setting or observed sender reaches it. |
| Reach | R3 | At least USD 10M per 30 days through the affected function, or at least USD 10M held behind it with use; or at least 5 % of validators or stake; or a component that most users of a layer depend on (a client, a relay, a major L2's node or prover). |
| Reach | R2 | Used in the last 90 days, and at least USD 100k per 30 days or held; or at least 0.5 % of validators or stake; or a widely used tool. |
| Reach | R1 | Used but small; or dormant with value still held; or reach not measured. |
| Reach | R0 | No use in 90 days and no value held. |
| Recovery | - | none (no fix after the fork) / governance (vote or timelock of days or more) / owner (one admin or multisig upgrade) / operator (release or config) / user (retry, wait). |

Trigger is rated on whether the path runs in live operation after the fork, assuming the mechanism holds. Every
post-fork behaviour is INFERRED (no 10 s network exists), so the evidence label does not lower the trigger. Doubt about
the mechanism itself goes in the evidence section, not in T.

Reach counts the value that goes through the affected function (per 30 days, per event, or held behind it), not the
protocol's total value or custody balance. The reverse also holds: a contract can hold USD 0 and still drive a large
flow, for example an oracle consensus contract that sets the value of a large staking pool.

## 3. Mapping

| Level | Rule (the first row that matches) |
|---|---|
| HIGH | I4 with T2+ and R2+. Or I3 with T2+, R3, and recovery none or governance. |
| MEDIUM | I4 or I3 with T1+ and R1+ (not HIGH). Or I2 with T2+ and R1+. |
| LOW | I2 with T1 or less, or R0. I3 or I4 with T0 or R0. Every I1. |
| NONE | I0. |

A safety window shorter than its design sizing is I2, so MEDIUM with T2+ and R1+.

**Dormancy rule.** A P2 note moves to P3 when a pinned read of the live binding shows no material current effect: the
system is empty or dormant, its settings cannot bind, or a funded time-based payout is immaterial. The note keeps its
effect and needs a recheck at T-6 months. Dormancy also gives R0.

## 4. Inflation checklist

Check each item before a MEDIUM or HIGH.

1. **Custody balance as value at risk.** Count the value through the affected function, not the total value.
2. **Operator software counted as unrecoverable.** An offchain daemon that the operator updates in a normal release is
   recovery `operator`, so at most I2, unless a wrong signed or onchain result stays after the update (I3 or I4).
3. **Drift with no safety role.** A voting period, vesting schedule or reward rate that runs 1/6 faster or slower is
   I1, unless the window protects value (challenge windows).
4. **Dormant or empty systems.** No use in 90 days and no value held is R0, so LOW at most.
5. **One model family counted as independent.** Two lenses from the same model family are one family.
6. **Recovery ignored.** A permissionless retry, an owner rescue, a pause or the next release lowers impact.
7. **A 12 in the code is not a path that runs.** Half of the top 60 text-census hits were code that does not run. The
   rating needs the path that runs on the live binding.
8. **The class rating given to each instance.** The class mechanism ("c = 12 lags 1,440 slots per day") does not rate an
   instance. Rate that system's function, setting and reach.
9. **The 8 s case used for the 10 s rating.** Rate at 10 s; the 8 s case is a paired note if its kind changes.
10. **A worst-case setting instead of the live one.** Rate the parameters set at the pinned block, not the largest value
    an admin could set.
11. **Lead time counted as impact.** A long governance path raises priority (P1), not impact.
12. **A wrong fix counted as impact.** "Set it to 10" breaking things is a separate risk. Rate the system as it is, and
    list the wrong fix in its own field.

## 5. Blind triage

- **Triager:** a different model family from the note's authors and lenses, or a human.
- **Packet:** the note's front matter without `impact`, `priority`, `lenses`, `status` and `triage`, and the body without
  the Rating and History sections. The words HIGH, MEDIUM, LOW, NONE and P1-P3 are redacted, together with the line
  that states the rating. The packet keeps the mechanism, the evidence and the numbers.
- **Isolation:** the triager runs in a directory that holds only this rubric and the packet, and reads nothing else.
- **Task:** first try to lower each axis. Is the loss really permanent? Does the path run in the live setting? Is the
  value per 30 days, or a custody balance? Is there a recovery path? Then write the four axes, one line each, and the
  level from section 3.
- **Output:** one row per note: original level, blind level, I, T, R, recovery, a one-line reason, and the checklist
  items that applied.
- **Changes:** a rating changes only through a reviewed pull request. A difference of two levels, or any change to a
  HIGH, gets a second reviewer.

## 6. Front-matter fields

See [schema/note.json](schema/note.json). For MEDIUM+ notes:

```yaml
impact_axes: "I3 T2 R1 recovery=owner"
reach_measure: "<value per 30 days or held, block, query>"
triage: "<model family or human>, blind, <date>, <level>"
```

## Open questions

1. Are the reach thresholds right (USD 10M and USD 100k; 5 % and 0.5 % of validators)?
2. Should a stop in a core client at the fork (I2, T3, R3) stay MEDIUM, as the table says, or be HIGH because many
   validators are hit at once? The table keeps it MEDIUM, and P1 carries the urgency.
3. Should a signed wrong result that a quorum could accept be I3 or I4? That depends on whether it can be corrected
   later.
