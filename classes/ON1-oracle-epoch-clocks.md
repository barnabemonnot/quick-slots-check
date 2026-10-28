# ON1: oracle-epoch clocks

Cause S1+S5. Worst seen: BREAKS, MEDIUM.

**Mechanism (CHECKED code; INFERRED timing).** A contract converts `block.timestamp` to an epoch on the 12 s grid, and
an offchain daemon supplies consensus-layer data for that epoch. After the fork the grid lags by Δ/60 slots. A daemon
that follows the grid reports data τ/6 old (5 d old after 30 d). A daemon that follows the real chain hits a deadline
gate and stops. Seen in the oracle stacks of several liquid-staking systems: first failures between 16.5 h and 5 d
after the fork; later stops in dependent modules from 56 d to 140 d.

**Fix (INFERRED).** A piecewise clock. Where the contract has a settable clock spec, set `G' = G + 64*e_F` and
`secondsPerSlot = 10` in one call (`G + 128*e_F` at 8 s), in the window from one oracle frame before `e_F` to a few
days after. An immutable spec needs a new implementation, together with every consumer (ON8).

**Wrong fixes.**
- `secondsPerSlot = 10` alone, with the old genesis: the epoch jumps about a year ahead. In one case a single report
  could then add 9.9-17.3 % of the pool's value.
- A new consensus-clock contract without matching oracle implementations: the switch reverts.
- Removing a deadline gate while the reference slot is still read as the beacon slot: reports count twice from about
  5.91 d.
- An admin call more than one oracle frame before `e_F`: the oracle stops before the fork.
- Treating 10 s as final before R9: 1,350 epochs wrong after 30 d if the value stays 12.

**Find.** `check/scan.py` rules SOL-SLOT-EPOCH-CONST, SOL-TIMESTAMP-DIV-12; search `secondsPerSlot`, `genesisTime`,
`refSlot`, `deadline`.

**Test.** At `T_F` the contract epoch must equal `e_F`. A report for the real data slot must pass the gate before and
after the fork, and each amount must enter accounting once.

**Lead time.** Settable spec: an admin call plus a daemon release; lands from `e_F` minus one frame to about `e_F` + 4
d. Upgradeable with a timelock: 3-5 weeks; queue by T-10 d. Immutable: new contracts, 9-103 d.
