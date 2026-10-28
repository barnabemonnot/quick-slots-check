# Quick Slots compatibility check

EIP-8198 ("Quick Slots") would shorten Ethereum slots from 12 seconds to 10 seconds. It is a candidate for the
Hegotá fork. **It is not scheduled.**

Code that assumes 12-second slots can stop or drift after such a fork. Most of it shares one bug: it converts between
slot and time with one fixed duration. This repository helps you check your own code before any fork:

- **Scan:** `python3 check/scan.py <path>` lists lines that may assume 12 s, with the class and the fix for each.
- **Test:** [vectors/](vectors/README.md) holds slot<->time test vectors and a reference implementation.
- **Fix:** [classes/](classes/README.md) and [checklists/](checklists/README.md) give the correct fix and the wrong
  fixes that look correct.
- **Specs:** [spec/](spec/README.md) holds proposed rule text for 14 spec gaps.

Start with [SUMMARY.md](SUMMARY.md). If you use a coding agent, point it at [AGENTS.md](AGENTS.md).

Found an affected live system? Write a note ([notes/](notes/README.md)), or report it privately first if you prefer
([SECURITY.md](SECURITY.md)). Evidence carries a label: CHECKED, INFERRED or UNVERIFIED.

Maintainer: Barnabé Monnot (@barnabemonnot). Status: early version, self-check track only. License: MIT
([LICENSE](LICENSE)).
