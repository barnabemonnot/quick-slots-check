# Onchain wrong fixes, by class (T-ON1a to T-ON8c)

28 wrong fixes seen in onchain systems. IDs and mechanisms are CHECKED from code reads; numeric forecasts are INFERRED
unless they are arithmetic. These are test instructions for isolated fixtures, not live transactions.

| ID | Find | Wrong fix and warning | Compatible change and test |
|---|---|---|---|
| T-ON1a | `secondsPerSlot`, `genesis` | Set 10 with the old `G`. At `e_F = 486000` the epoch jumps by 97,200. | An anchored schedule, with an atomic parameter change; assert epoch continuity at `F`. |
| T-ON1b | consensus-contract setters, config-mismatch errors | Replace the consensus clock contract alone; its 10 s config disagrees with oracle immutables. | Deploy matching oracle implementations; test one valid report through every oracle. |
| T-ON1c | `refSlot`, `deadline` | Remove a gate but keep "beacon slot = reference slot". Repeated accounting from about 5.91 d. | Map the grid reference to the real data slot; assert each amount enters accounting once. |
| T-ON1d | elapsed-time and annual-increase limits | Catch up with a one-frame elapsed time. After about 14 d a 3 % APR case exceeds a 10 % sanity cap. | Verified elapsed time and a catch-up plan that keeps sanity checks; test a gap beyond 14 d. |
| T-ON1e | `genesis`, `secondsPerSlot`, `finalized` | Activate the new clock early. A settable spec stops before `e_F` minus one 24 h frame. | Ship early, activate in the class window; check finality before, at and after `F`. |
| T-ON1f | `FORK_EPOCH`, `secondsPerSlot` | Assume 10 s is final. Actual 12 s gives a 1,350-epoch error after 30 d. | Freeze the value with the epoch (R9); rerun vectors when either changes. |
| T-ON1g | `refSlot`, `updatedAt`, `updateRate` | Change the meaning of the reference slot alone. Downstream rate updates fail after 5.0 d. | Apply T-ON8a; verify a report after day 5. |
| T-ON2a | `genesis`, `slot`, `* 10` | `G + 10*s` for all history. At `F` the timestamp error is 2F seconds. | Real block timestamps with proved slots, or the anchored schedule. |
| T-ON2b | `8191`, proof timestamp, last balance or slot | Trust a comment's slot-age bound and remove an accounting check. Accepted age reaches 9,829 slots. | Keep root, freshness and accounting checks; reject repeated accounting. |
| T-ON3a | `fork_version`, `signature_slot`, `/ 12` | Fork-version-only update; the 12 s guard rejects fresh updates. | Ship version and clock together; accept an update at `T_F + 60 s`. |
| T-ON3b | `seconds_per_slot`, checkpoint-age checks | A constant 10 from genesis. The example jumps 3.46 million slots. | The schedule for current slot and checkpoint age; test bootstrap at a realistic `F`. |
| T-ON3c | `SECONDS_PER_SLOT`, client creation, `config/spec` | Store one API duration as a full-history clock (1,440 slots per day lost). | Store the validated schedule; test both legacy-value responses. |
| T-ON3d | base head, `MAX_SLOT_AGE`, slot timestamp | Treat an old-base-head workaround as permanent. Proof span 5.3 sync periods after 30 d. | Install the fork-aware prover and verifier; keep the intended age rule. |
| T-ON4a | confirm, challenge and grace periods in blocks | Change confirmation only. An unchanged 45,818-block challenge lasts 5.30 d. | Update the whole challenge configuration; replace components with immutable periods. |
| T-ON4b | `FORK_TIME`, `execute` | Vote a fixed date too soon. A correction can need another 34-37 d path. | Runtime parameters or a validated fork gate; rehearse a moved date. |
| T-ON4c | `block.number`, `block.timestamp` | Change counter units without migration. Stored L1 deadlines can expire at once. | Keep the counter and rescale, or migrate every deadline. |
| T-ON4d | withdrawal-delay constants | Raise one delay, keep its mirror. Early completion attempts revert. | Apply T-ON8b to both contracts. |
| T-ON5a | `clock(`, `CLOCK_MODE`, `proposalDeadline` | Switch a governor to seconds while proposals store block deadlines. An open vote changes state at once. | Keep the block clock and rescale, or migrate with no open proposals. |
| T-ON5b | `setVotingPeriod`, `setVotingDelay` | Run setters at `F`. Existing proposals keep windows 16.7 % shorter after the fork. | Run them at `T_F - 5.25 d` to `T_F - 3.25 d`. |
| T-ON5c | `MAX_VOTING`, `MIN_VOTING`, `1 days / 12` | Declare all bounded setters unusable. All 58 bounded sample rows accept x1.2. | Inspect the bounds; apply valid setters. |
| T-ON6a | time-based accrual switch, `accrualBlockNumber` | Read a block checkpoint as seconds: 55-66 years of interest at once. | Keep block accrual and scale the rate, or migrate checkpoints and rates together. |
| T-ON6b | L1 block counter, `accrualBlockNumber` | Change one market's counter. A simulation gives x4.48 borrows in one accrual. | Keep the clock or migrate all markets together. |
| T-ON6c | `eta`, `queue`, `execute`, rate-model setters | Queue an unguarded rate change early. It can activate 14 d before the fork. | Put the fork condition inside the action; test no pre-fork change. |
| T-ON7a | L1 slot-duration constants, slot-duration validation | Set the node's duration alone to 10. `72 % 10 = 2`, so validation fails. | Coordinate config, align the grid with real L1 time; test 8 s separately. |
| T-ON7b | `4444444444444445`, `epochs` | Change one side of epoch pricing. 225 epochs become 20 h and the model disagrees. | Apply T-ON8c. |
| T-ON8a | `refSlot`, `updatedAt`, `updateRate` | Fix the producer but keep bridge or pusher `G+12s`. Rate updates stop after 5.0 d. | Replace all consumer implementations with the producer change; test day 6. |
| T-ON8b | withdrawal-delay constants, completion calls | Keep a local mirror while the upstream delay rises to 120,960 blocks. | Update both delays; test queues at upstream eligibility. |
| T-ON8c | `4444444444444445`, `epochs` | The model counts fewer tickets than the unchanged contract (46.86 tickets in one example). | Align historical and new pricing in both components. |
