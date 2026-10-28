---
id: R3
title: Stable duration key
priority: P1
decides: consensus-specs and beacon-APIs authors
latest_decision: select at T-12 to T-9 months; freeze before the first public-testnet release
depends_on: [R2]
---

# R3: key names and refusal

**Gap (CHECKED).** The duration key has had three names so far (`SLOT_DURATION_SCHEDULE`, then
`SLOT_DURATION_MS_EIP8198`, then `SLOT_DURATION_MS_HEZE` in open drafts). Config-file readers in four CL client
branches accept a missing or misnamed key and keep a default. Two tools read old names and fall back to 12 s.

**Why it matters (INFERRED).** The default depends on the preset. On mainnet with base 12000, all four branches keep
12 s. On the minimal preset, one branch falls back to 5 s while three keep 6 s. A file-configured devnet or testnet
can split at the Heze epoch. A native loader test of one branch also found that YAML type errors and valid
indentation variants can activate defaults (CHECKED in a local build; no network outcome was run).

## Proposed rule text (INFERRED)

For consensus-specs Heze configs and beacon-APIs compatibility rules:

> The canonical key is `SLOT_DURATION_MS_HEZE`, paired with `HEZE_FORK_EPOCH`. The name MUST be fixed no later than
> the first client release that schedules Heze on a public testnet.
> If `HEZE_FORK_EPOCH != FAR_FUTURE_EPOCH`, the validated network configuration MUST contain a valid
> `SLOT_DURATION_MS_HEZE`, also when its value equals the legacy duration.
> A consensus client MUST reject a configuration that lacks this value. It MUST NOT substitute `SLOT_DURATION_MS`, a
> preset default or a value inferred from the current time. A loader MUST check supplied external configuration
> before default insertion can hide a missing or misnamed key.
> A beacon API consumer that uses the per-fork form MUST reject a scheduled Heze fork with no valid duration key. A
> schedule consumer need not decode names of unknown future forks to use their schedule rows.
> Rejection MUST name the network, fork and missing or invalid field. Logging an error while continuing
> time-sensitive work with a default is not rejection.
> A validator client MUST compare its normalized schedule with each beacon node before using it for duties, and after
> reconnect or a schedule update. On mismatch it MUST refuse that node for duties.
> A later rename MUST keep the previous name as an alias through at least one later network upgrade. If both are
> present, their values MUST agree; otherwise the configuration MUST be rejected. An array and a scalar MUST NOT be
> treated as direct aliases.
> A beacon node MUST NOT remove a compatibility key in the same release series that introduces a slot-duration change.
> Configuration tests MUST include a scheduled fork with a duration different from the legacy value, a missing key, a
> misnamed key and conflicting aliases. The missing and misnamed cases MUST fail before default insertion.

**Wrong fix (INFERRED).** Checking positivity or units only after YAML decoding can miss a malformed known value that
was left at its preset default. A raw text-prefix check misses valid equivalent YAML. Parse the mapping first, choose
the preset, then validate critical fields before the configuration becomes active.

## Alternatives (INFERRED)

(a) freeze `_HEZE` (preferred: the checked client branches use it); (b) pick another name before the public-testnet
release and migrate all producers and consumers together; (c) rely on the schedule for generic consumers, with strict
per-fork consensus configuration.

## Open (UNVERIFIED)

Approval of `_HEZE`; any alias from `_EIP8198`; the deprecation interval after Heze.

Test: the `config` kind in [vectors/](../vectors/README.md) (`--self-test`).
