# ON3: beacon light clients on other chains

Cause S1. Worst seen: BREAKS, MEDIUM.

**Mechanism (CHECKED code; INFERRED timing).** The client asserts `current_slot >= update.signature_slot` with a local
clock. `(now - G)/12` rejects fresh updates once the real slot passes it. One onchain client underflows after
4.76-5.00 h (2.34-2.86 h at 8 s); its prover rejects from about 1-2 min. Clients without this guard are BENIGN. One
bridge relayer waits until its local clock passes the signature slot, so fresh-header waits can time out at about
`T_F + 74 min` (about 30 min at 8 s), depending on snapshot age and polling.

**Fix (INFERRED).** A fork-aware clock in the same release as the Heze fork version, used for every clock use. Where a
contract stores the light-client address as immutable, a new client also needs an upgrade of its consumer.

**Wrong fixes.** A fork-version-only release. A constant 10 from genesis (the guard never fires). Keeping an old base
head as a workaround: it works for months, but the proof span grows and an age guard stops holding.

**Find.** SOL-TIMESTAMP-DIV-12, GEN-DIV-12-FROM-GENESIS; search `signature_slot`, `fork_version`, `/ 12`.

**Test.** Accept a valid update signed at `T_F + 60 s`; still reject a future signature.

**Lead time.** Release plus verifying-key update; a new client contract plus 1-2 months.
