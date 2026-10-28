# Hunting: closed

The hunting track, where anyone's agents look for affected systems that belong to others, is **closed** in this
version.

Why:

- **Triage capacity is the bottleneck, not search.** In earlier work, half of the top text-census hits were code that
  does not run, and 7 of 20 top "BREAKS" calls were refuted on review. Every report needs a careful, blind triage. No
  owner and capacity for that triage has been agreed yet.
- **Disclosure needs a plan.** Owners must hear about their system in private first. The process for that is not set.
- **The self-check track is cheaper.** Teams that check their own code need no triage and fix faster.

What to do instead:

- Check your own systems with [check/scan.py](check/scan.py), [vectors/](vectors/README.md) and
  [checklists/](checklists/README.md).
- If you already know of an affected live system, report it privately: [SECURITY.md](SECURITY.md).

Do not open issues or pull requests that list other people's affected systems. They will be closed.

When hunting opens, this file will describe the classes to look for, the populations not yet covered, a mechanical
submission bar checked by CI, and the private intake. That needs a maintainer decision first.
