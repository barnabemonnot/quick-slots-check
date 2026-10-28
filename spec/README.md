# Spec gaps R1-R14

One file per gap. IDs are stable: cite them as R1 ... R14. EIP-8198 is a candidate and is not scheduled.

A **spec gap** is something that EIP-8198 or the specs (consensus-specs, beacon-APIs, execution-apis) do not say
today. The existence of each gap is CHECKED against the spec text read on 2026-10-22 to 2026-10-24. Every proposed
rule is INFERRED: it is a design proposal, not an adopted rule. In paste text, MUST, MUST NOT, SHOULD, SHOULD NOT and
MAY have their RFC 2119 / RFC 8174 meanings.

Priority for spec gaps: **P1** = adopt rule text at T-12 to T-9 months; **P2** = settle before the first client
releases (about T-30 d); **P3** = fix the text when convenient.

| ID | File | Priority | Who decides |
|---|---|---|---|
| R1 | [R01-slot-time-formula.md](R01-slot-time-formula.md) | P1 | EIP authors; consensus-specs |
| R2 | [R02-beacon-api-schedule.md](R02-beacon-api-schedule.md) | P1 | beacon-APIs; CL client teams |
| R3 | [R03-stable-duration-key.md](R03-stable-duration-key.md) | P1 | consensus-specs; beacon-APIs |
| R4 | [R04-4788-migration.md](R04-4788-migration.md) | P2 | ACD; EL client teams |
| R5 | [R05-4788-eviction-text.md](R05-4788-eviction-text.md) | P2 | EIP authors |
| R6 | [R06-2935-history-window.md](R06-2935-history-window.md) | P3 | EIP authors |
| R7 | [R07-request-fee-dynamics.md](R07-request-fee-dynamics.md) | P3 | EIP authors |
| R8 | [R08-provisional-fork-epoch.md](R08-provisional-fork-epoch.md) | P1 | ACD |
| R9 | [R09-freeze-slot-value.md](R09-freeze-slot-value.md) | P1 | ACD |
| R10 | [R10-el-fork-bpo-time.md](R10-el-fork-bpo-time.md) | P2 | EL configuration authors |
| R11 | [R11-engine-api-simulate-text.md](R11-engine-api-simulate-text.md) | P3 | execution-apis |
| R12 | [R12-light-client-duty-clock.md](R12-light-client-duty-clock.md) | P2 | consensus-specs |
| R13 | [R13-retention-weak-subjectivity.md](R13-retention-weak-subjectivity.md) | P2 | consensus-specs; EIP authors |
| R14 | [R14-blob-gas-base-fee.md](R14-blob-gas-base-fee.md) | P2 | ACD |

Smaller items not drafted here: R15 (confirm each intra-slot deadline in basis points of the slot), R16 (align the
EIP text with consensus-specs in six places) and R17 (minor prose; list the affected classes in Backwards
Compatibility).

To discuss a gap, open a "spec gap" issue. Do not use issues to report a named system: see [SECURITY.md](../SECURITY.md).
