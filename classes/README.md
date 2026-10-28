# Classes of affected systems

One file per class. IDs are stable. Onchain classes are ON1-ON8 (earlier drafts wrote them O1-O8); offchain classes
are OFF1-OFF7. A class describes a mechanism. It does not rate any one system: rate an instance with
[RATING.md](../RATING.md).

Cause codes: **S1** hard-coded 12 s slot arithmetic; **S2** block number used as a clock; **S3** per-block rate;
**S4** protocol system contracts (EIP-4788, EIP-2935, EIP-7002/7251); **S5** an offchain assumption that onchain code
depends on; **S6** other.

Effect: **BREAKS** = stops or gives wrong results; **DRIFTS** = correct, but the wall-clock meaning changes;
**BENIGN** = no change. "Worst effect" is the worst rating seen in the class (CHECKED mechanism; INFERRED timing).

| ID | Class | Cause | Worst effect | First failure at 10 s, if nobody acts |
|---|---|---|---|---|
| [ON1](ON1-oracle-epoch-clocks.md) | Oracle-epoch clocks | S1+S5 | BREAKS, MEDIUM | 16.5 h to 5 d |
| [ON2](ON2-4788-computed-timestamp.md) | EIP-4788 consumers that compute a timestamp | S1+S4 | BREAKS, MEDIUM | first post-fork proof |
| [ON3](ON3-onchain-light-clients.md) | Beacon light clients on other chains | S1 | BREAKS, MEDIUM | about 1 min (prover); 4.76 h (onchain) |
| [ON4](ON4-block-count-security-windows.md) | Block-count security windows | S1/S2 | BREAKS, HIGH mechanism | x5/6 from the fork |
| [ON5](ON5-block-count-governance-windows.md) | Block-count governance windows | S2 | DRIFTS, LOW | x5/6 from the fork |
| [ON6](ON6-per-block-rates.md) | Per-block rates and caps | S3 | DRIFTS, LOW | x1.2 per second from the fork |
| [ON7](ON7-fixed-12s-grids.md) | Fixed 12 s grids and folded constants | S1+S5 | BREAKS, MEDIUM | at once |
| [ON8](ON8-paired-constants.md) | Paired constants | S1/S2 | BREAKS, MEDIUM | after a one-sided fix |
| [OFF1](OFF1-duty-clients-dvt.md) | Validator duty clients and distributed validators | S1/S5 | BREAKS, MEDIUM | 20-60 s |
| [OFF2](OFF2-l2-nodes-proof-hosts.md) | L2 nodes, proof hosts, L2 consensus inputs | S1/S6 | BREAKS, MEDIUM | first post-fork blob batch |
| [OFF3](OFF3-light-clients-relayers.md) | Beacon light clients, provers, relayers | S1 | BREAKS, MEDIUM | 52-95 s |
| [OFF4](OFF4-staking-daemons.md) | Staking oracle daemons, provers, keepers | S1/S5 | BREAKS, MEDIUM | 1.7 h to 5.07 d |
| [OFF5](OFF5-pbs.md) | PBS: relays, builders, sidecars | S1 | BREAKS, MEDIUM | slot F+1 |
| [OFF6](OFF6-shared-libraries.md) | Shared libraries and SDKs (carriers) | S1 | wrong-fix carrier | through dependents |
| [OFF7](OFF7-monitoring-ui.md) | Monitoring, explorers, indexers, UIs | S1 | BREAKS, LOW | from 25 min |
| [-](no-breaks.md) | Robust designs that do not break | - | DRIFTS, LOW | - |

No class has a CRITICAL finding.

Two numbers recur (CHECKED arithmetic):

1. A 12 s clock lags the real slot by Δ/60 slots at 10 s (Δ/24 at 8 s): 1,440 slots per day (3,600). Data that a 12 s
   grid selects τ after the fork is τ/6 old (τ/3).
2. A 10 s clock anchored at genesis runs 0.2F slots ahead (0.5F at 8 s), that is 2F seconds (4F s): 370-456 d
   (740-913 d) for a fork between 2027-01 and 2028-06.

Quick reference (CHECKED arithmetic):

| Quantity | 10 s | 8 s |
|---|---|---|
| Epoch of 32 slots | 384 -> 320 s | 384 -> 256 s |
| N slots | 12N -> 10N s (x5/6) | 12N -> 8N s (x2/3) |
| Unchanged rate per block | x1.2 per unit time | x1.5 per unit time |
| Window count to keep seconds | x1.2, round up | x1.5, round up |
| Rate per block to keep per-second | x5/6 | x2/3 |
| Virtual genesis `G'` | `G + 64*e_F` | `G + 128*e_F` |
| Youngest EIP-4788 root evicted early | 16,382 s (4 h 33 m) | 32,764 s (9 h 06 m) |

A 12 -> 9 s public devnet exists: there, epochs are 288 s, a 12 s clock lags 2,400 slots per day, and `G' = G + 96*e_F`.
Do not reuse 10 s numbers on that network.
