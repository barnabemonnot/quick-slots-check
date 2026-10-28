# Notes

One note per instance of a class, with front matter that follows [schema/note.json](../schema/note.json). This folder
is empty in the first version: notes on named systems are not published yet, and class-level notes are added only
after review.

Copy [schema/examples/valid-ON1-001.md](../schema/examples/valid-ON1-001.md) to start. File name: `<id>.md`, for
example `ON1-001.md`. Body sections: Summary, Mechanism, Evidence, Compatible change, History.

Rules for a note here:

- It names no system while `disclosure: class-level`: `addresses` and `repos` stay empty, and
  `python3 tools/names_check.py` passes.
- Every claim carries CHECKED, INFERRED or UNVERIFIED.
- Ratings follow [RATING.md](../RATING.md). A MEDIUM or HIGH note needs `impact_axes` and `reach_measure`.
- No exploit write-up: mechanism and timing, not a strategy.

If your note would name a live system, do not open a pull request. Use a private security advisory instead
([SECURITY.md](../SECURITY.md)).

Check before you push: `python3 tools/validate.py`.
