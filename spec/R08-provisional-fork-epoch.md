---
id: R8
title: Provisional fork epoch
priority: P1
decides: ACD
latest_decision: T-60 d at the latest
depends_on: [R9, R14]
---

# R8: fork epoch notice

**Gap (CHECKED).** No process rule gives enough notice for changes that need the fork epoch.

**Why it matters (CHECKED history and onchain minimums).** In six forks the final epoch came 26-34 d before the fork;
one fork had a provisional epoch 75 d before. One rollup DAO path takes 34.5-36.7 d onchain (at least 42 d with its
phases). One staking governance path takes 57.2 d with one veto cycle. L2 fault-proof prestates took about 5 weeks.
INFERRED: these paths do not fit 26-34 d if they need the fork time as a constant.

## Proposed rule text (INFERRED)

For the ACD upgrade process; link from EIP-8198 Transition parameters:

> The upgrade coordinators MUST publish a provisional mainnet fork epoch at least 60 days before its derived
> activation time. One day means 86400 seconds.
> The publication MUST identify the network, genesis time, fork version, epoch, `FORK_SLOT`, `FORK_TIME`, duration in
> milliseconds, configuration revision and decision status. The duration MUST already be frozen under R9.
> A provisional epoch MUST be marked provisional and MUST NOT be presented as authority to activate a production
> network.
> Coordinators SHOULD arrange review of changes that depend on these parameters before the provisional publication.
> An earlier replacement epoch MUST meet the same 60-day notice. A later replacement epoch MUST include a revised
> impact review.
> A final epoch publication MUST say which provisional parameters it confirms or replaces.
> If the chosen blob-fee design requires L2 fault-proof artifacts that embed the activation time, the final time MUST
> be available at least 35 days before activation.
> If the notice or a dependent release path cannot be met, coordinators MUST move activation to a later epoch.

For EIP-8198 Backwards Compatibility:

> Application upgrades SHOULD separate code deployment from fork-parameter activation. Where parameters can change, the
> epoch and duration SHOULD be supplied as one validated update under the application's authorization and delay
> rules. Applications SHOULD use protocol slot data where available. They MUST NOT assume that a provisional epoch is
> immutable.

## Alternatives (INFERRED)

Keep the historical final-epoch window and require every consumer to avoid embedded time; freeze a final epoch at
T-60 d; or publish a provisional epoch at T-60 d and confirm it later (selected).

## Open (UNVERIFIED)

ACD must adopt the rule, name the publication authority, and decide whether R14 needs the 35-day final-time rule.
