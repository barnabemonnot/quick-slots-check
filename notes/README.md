# Notes

One note per instance of a class, with front matter that follows [schema/note.json](../schema/note.json). This folder
is empty in the first version. Notes may name the system, its team, its addresses and its code.

Copy [schema/examples/valid-ON1-001.md](../schema/examples/valid-ON1-001.md) to start. File name: `<id>.md`, for
example `ON1-001.md`. Body sections: Summary, Mechanism, Evidence, Compatible change, History.

Rules for a note here:

- It binds the claim to a pinned block (for contracts: proxy and implementation) or a release (for software), in
  `addresses`, `repos` and the Evidence section.
- It is factual: mechanism, evidence and fix. No blame, no speculation about intent.
- Every claim carries CHECKED, INFERRED or UNVERIFIED.
- Ratings follow [RATING.md](../RATING.md). A MEDIUM or HIGH note needs `impact_axes` and `reach_measure`.
- No exploit write-up: mechanism and timing, not a strategy.

If you would rather the owner hears first, use a private security advisory ([SECURITY.md](../SECURITY.md)); the
maintainer can contact the owner before the note is published.

Check before you push: `python3 tools/validate.py`.
