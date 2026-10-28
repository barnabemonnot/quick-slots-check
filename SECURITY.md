# Security and private reports

## Reporting an affected system

Naming an affected system in a public note is allowed ([notes/](notes/README.md)). Use a private report instead when
you would rather the owner hears first, or when you are not sure your claim holds. To report privately, open a GitHub
private security advisory on this repository:

1. Go to the repository's **Security** tab.
2. Choose **Report a vulnerability**.
3. Fill in the advisory. Only the maintainer and the people he invites can see it.

Include, as far as you have it:

- the class ([classes/](classes/README.md)) and the mechanism, with the slot arithmetic at 10 s;
- the live binding at a pinned block or release (for contracts: proxy and implementation; for software: the release
  operators run);
- the path that runs, and why;
- a reproduction: a model, a fork test or a vector run;
- the rubric axes from [RATING.md](RATING.md), with a measure of reach if you have one;
- an evidence label on every claim.

## What happens next

- The maintainer, Barnabé Monnot (@barnabemonnot), acknowledges the advisory. He has not yet set response times.
- A triager from a different model family, or a human, rates it blind under [RATING.md](RATING.md).
- The maintainer decides whether to contact the owner first, and when the report becomes a public note.

## Rules for reporters

- Read-only on live networks. Never send a transaction to test a claim.
- No exploit write-ups or attack strategies. Mechanism and timing are enough.
- Do not contact the owner in the name of this repository.

EIP-8198 is not scheduled, so no finding here can be exploited today.

## Security of this repository

For a problem with the repository itself, such as a leaked key or a malicious change to a workflow, also use a
private advisory.
