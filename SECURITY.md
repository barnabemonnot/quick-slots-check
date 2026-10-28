# Security and private intake

## Report a named system privately

If your report names a live system (a team, project, product, protocol, client, chain other than Ethereum, company,
person or contract address), **do not open a public issue or pull request.** Use a GitHub private security advisory
on this repository:

1. Go to the repository's **Security** tab.
2. Choose **Report a vulnerability**.
3. Fill in the advisory. Only the maintainers and people they invite can see it.

Include, as far as you have it:

- the class ([classes/](classes/README.md)) and the mechanism, with the slot arithmetic at 10 s;
- the live binding at a pinned block or release (for contracts: proxy and implementation; for software: the release
  operators run);
- the path that runs, and why;
- a reproduction: a model, a fork test or a vector run;
- the rubric axes from [RATING.md](RATING.md), with a measure of reach if you have one;
- an evidence label on every claim.

## What happens next

- The maintainers acknowledge the advisory. Response times are **pending decision**.
- A triager from a different model family, or a human, rates it blind under [RATING.md](RATING.md).
- The maintainers decide whether and when to contact the owner. Owners hear first in private, not on GitHub.
- A named note is published only after the owner has been contacted, or at a disclosure date set by the
  maintainers. Until then, at most a class-level count appears in public.

## Rules for reporters

- Read-only on live networks. Never send a transaction to test a claim.
- No exploit write-ups or attack strategies, even in a private advisory. Mechanism and timing are enough.
- Do not contact the owner in the name of this repository.

EIP-8198 is not scheduled, so no finding here is exploitable today. Private intake still applies, so that owners do
not first hear about their system in public.

## Security of this repository

For a problem with the repository itself (for example a leaked key or a malicious workflow change), also use a
private advisory.
