---
id: R7
title: EIP-7002 and EIP-7251 request-fee dynamics
priority: P3
decides: EIP-8198 authors
latest_decision: when convenient
depends_on: []
---

# R7: request-fee dynamics

**Gap (CHECKED).** EIP-8198 does not state how the EIP-7002 (withdrawal request) and EIP-7251 (consolidation
request) fee mechanisms change with shorter slots.

**Mechanism (CHECKED, local execution of the published bytecode).** The contracts update `excess` once per system call,
from the requests added, and keep a 1-wei fee floor. With a block every 10 s, the per-second target and the fee decay
both run x1.2 faster. ETH throughput is unchanged. Callers read the fee in the same transaction. Effect: BENIGN.

INFERRED: the x1.2 figure assumes a block every 10 s; missed slots add no update. For an `excess = 80` fixture, the fee
falls from 109 to 54 wei in 6 of 12 produced blocks (60 s of 120 s at 10 s).

## Proposed text (INFERRED)

State the x1.2 per-second effect and that throughput is unchanged. Keep the constants. A fee-constant change would need
code replacement at the existing address.
