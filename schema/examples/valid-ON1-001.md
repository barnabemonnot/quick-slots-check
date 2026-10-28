---
title: An oracle-epoch clock in a synthetic staking oracle
id: ON1-001
layer: onchain
chain: mainnet
addresses: []
repos: []
class: ON1
cause: S1+S5
effect: BREAKS
impact: MEDIUM
priority: P1
at_10s: the deadline gate closes about 5 d after the fork
at_8s: same kind, about 2 d
fix: piecewise clock set with G' and d in one call
common_wrong_fix: secondsPerSlot = 10 with the old genesis
fix_layer: onchain config
who_acts: the contract owner
timing: from one oracle frame before the fork epoch to 4 d after
depends_on_spec: R1, R9
status: open
evidence: INFERRED
reproduction: none
impact_axes: I2 T3 R2 recovery=owner
reach_measure: synthetic example, no measurement
---

Synthetic example for tools/validate.py --self-test. It describes no real system.
