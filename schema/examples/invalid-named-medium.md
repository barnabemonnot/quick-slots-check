---
title: A MEDIUM note without rubric axes
id: OFF4-001
layer: offchain
chain: n/a
repos: [someorg/somerepo@abc123 src/clock.go:10]
class: OFF4
cause: S1
effect: BREAKS
impact: MEDIUM
priority: P2
at_10s: stops after 1 d
fix: read the schedule at run time
common_wrong_fix: none known
who_acts: operators
timing: before the fork
status: open
evidence: CHECKED
reproduction: none
---

Synthetic negative example: must fail (no impact_axes or reach_measure for MEDIUM).
