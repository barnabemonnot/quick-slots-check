# OFF6: shared libraries and SDKs (carriers)

Cause S1. Worst seen: carries wrong fixes into dependents.

**Mechanism (CHECKED code).** A library exposes one duration: a clock constructor that takes one `d`, a
`SlotDuration()` or `SECONDS_PER_SLOT` getter, or a `chaintime` helper that others copy. In unreleased Heze branches of
CL clients, some constructors keep a one-entry schedule and some getters keep the genesis value, while the clock itself
becomes piecewise. Dependents then fail to build, and a naive port keeps 12 s. One copied helper is used in four
projects. Common EVM libraries hold 12 s constants that only drift.

**Fix (INFERRED).** Deprecate every single-duration API. The positive pattern: keep the function name and make it
piecewise.

**Wrong fixes.** A naive port that passes one constant to the clock constructor. A library bump that is expected to fix
the dependents.

**Find.** GEN-SINGLE-DURATION-API, GEN-SLOT-DURATION-12.

**Test.** Compile and run the [vectors](../vectors/README.md) through each real caller, not only the library.

**Lead time.** Library release, then each dependent's release.
