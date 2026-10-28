#!/usr/bin/env python3
"""Hygiene check: no machine-local paths, keys, addresses or compiled files in the repository.

  python3 tools/hygiene.py            # check every file under the repository root
  python3 tools/hygiene.py PATH ...   # check given files or folders

A line that must contain a matching string (for example a rule in this file) carries the marker `hygiene: allow`.
Addresses are checked by tools/names_check.py (run it without a denylist for the address check alone).
Exit 0 = clean; 1 = at least one hit.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALLOW = "hygiene: allow"
RULES = [  # hygiene: allow
    ("home path", re.compile(r"(/(Users|home)/[A-Za-z][A-Za-z0-9_.-]*|(^|[\s\"'=(:`])/root/|(^|[\s\"'=(])~/[A-Za-z])")),  # hygiene: allow
    ("temp or scratch path", re.compile(r"/private/(tmp|var)/|/tmp/[A-Za-z]+-[0-9]+/|/var/folders/")),  # hygiene: allow
    ("key in URL path", re.compile(r"https?://[^\s/]+(/[a-z0-9_-]+)?/v[0-9]+/[A-Za-z0-9_-]{24,}")),  # hygiene: allow
    ("api key parameter", re.compile(r"(?i)(api[_-]?key|apikey|access[_-]?token)=[A-Za-z0-9_-]{16,}")),  # hygiene: allow
    ("bearer token", re.compile(r"(?i)authorization:\s*bearer\s+[A-Za-z0-9._-]{16,}")),  # hygiene: allow
    ("GitHub token", re.compile(r"\b(gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b")),  # hygiene: allow
    ("LLM API key", re.compile(r"\bsk-(ant-)?[A-Za-z0-9_-]{20,}")),  # hygiene: allow
    ("chat token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),  # hygiene: allow
    ("cloud key id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),  # hygiene: allow
    ("private key value", re.compile(r"(?i)private[_-]?key\s*[=:]\s*['\"]?0x[0-9a-f]{64}\b")),  # hygiene: allow
    ("private key block", re.compile(r"BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY")),  # hygiene: allow
    ("path into a working repository", re.compile(r"(^|[\s(\[`'\"])\.{0,2}/?(reports|findings|inbox)/[A-Za-z0-9_.-]+")),  # hygiene: allow
    ("local hostname", re.compile(r"\b[A-Za-z0-9-]+\.(local|lan|internal)\b(?![-.\w])")),  # hygiene: allow
]
SKIP_DIRS = {".git"}


def iter_files(paths):
    for p in paths:
        p = Path(p)
        if p.is_file():
            yield p
            continue
        for f in sorted(p.rglob("*")):
            if f.is_file() and not (set(f.relative_to(p).parts) & SKIP_DIRS):
                yield f


def main(argv):
    paths = argv or [str(ROOT)]
    bad = 0
    for f in iter_files(paths):
        if "__pycache__" in f.parts or f.suffix in (".pyc", ".pyo"):
            bad += 1
            print(f"{f}: compiled Python file")
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for n, line in enumerate(text.splitlines(), 1):
            if ALLOW in line:
                continue
            for name, rx in RULES:
                m = rx.search(line)
                if m:
                    bad += 1
                    print(f"{f}:{n}: {name}: {m.group(0)[:60]}")
    print(f"hygiene: {bad} hit(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
