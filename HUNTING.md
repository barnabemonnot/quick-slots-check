# Hunting: closed for now

The hunting track is **closed** in this version. In that track, anyone's agents look for affected systems that
belong to others. Whether and when it opens is the maintainer's decision (Barnabé Monnot).

Why it is closed:

- **Triage capacity is the bottleneck, not search.** In earlier work:
  - half of the top text-census hits were code that does not run;
  - 7 of 20 top "BREAKS" calls were refuted on review.

  Every report needs a careful, blind triage. No owner or weekly capacity for that triage has been set yet.
- **The self-check track costs less.** Teams that check their own code need no triage, and they fix faster.

What to do instead:

- Check your own systems with [check/scan.py](check/scan.py), [vectors/](vectors/README.md) and
  [checklists/](checklists/README.md). Write up the result as a note ([notes/](notes/README.md)).
- If you already know of an affected system, write a note with the evidence, or report it privately
  ([SECURITY.md](SECURITY.md)).

Do not open bulk lists of other people's systems from scanner hits. They will be closed.

When hunting opens, this file will describe:
- the classes to look for;
- the populations not yet covered;
- a mechanical submission bar checked by CI: live binding at a pinned block, the path that runs, the slot
  arithmetic, a reproduction, the rubric axes with reach, and a check against known coverage.
