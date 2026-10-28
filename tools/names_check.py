#!/usr/bin/env python3
"""Fail if the repository names a system or holds an address.

This repository describes classes and counts. It names no team, project, product, protocol, client implementation,
chain other than Ethereum, company, person or contract address.

  python3 tools/names_check.py                       # addresses only
  python3 tools/names_check.py --denylist FILE       # addresses and every term in FILE
  python3 tools/names_check.py --denylist FILE PATH  # check one file or folder

The denylist is kept outside this repository, because the list itself would name systems. Format: one term per line;
`#` starts a comment; a term matches case-insensitively as a whole word; a `cs:` prefix makes it case-sensitive.

Exit 0 = clean; 1 = at least one hit; 2 = usage error.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ADDRESS = re.compile(r"(?<![0-9A-Za-z])0x[0-9a-fA-F]{40}(?![0-9a-fA-F])")
# Protocol system contracts whose addresses are fixed in EIP text (EIP-4788, EIP-2935, EIP-7002, EIP-7251).
# They are spec constants, not deployed systems of any team.
SPEC_ADDRESSES = {
    "0x000f3df6d732807ef1319fb7b8bb8522d0beac02",  # EIP-4788 beacon roots
    "0x0000f90827f1c53a10cb7a02335b175320002935",  # EIP-2935 history
    "0x00000961ef480eb55e80d19ad83579a64c007002",  # EIP-7002 withdrawal requests
    "0x0000bbddc7ce488642fb579f8b00f3a590007251",  # EIP-7251 consolidation requests
}
SKIP_DIRS = {".git", "__pycache__"}
TEXT_SUFFIXES = {".md", ".py", ".json", ".yml", ".yaml", ".txt", ".sol", ".go", ".rs", ".ts", ".js", ""}


def load_denylist(path):
    rules = []
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        term = raw.strip()
        if not term or term.startswith("#"):
            continue
        flags = re.I
        if term.startswith("cs:"):
            term, flags = term[3:], 0
        rx = re.compile(r"(?<![A-Za-z0-9])" + re.escape(term) + r"(?![A-Za-z0-9])", flags)
        rules.append((term, rx))
    return rules


def files(paths):
    for p in paths:
        p = Path(p)
        if p.is_file():
            yield p
            continue
        for f in sorted(p.rglob("*")):
            if f.is_file() and not (set(f.relative_to(p).parts) & SKIP_DIRS) and f.suffix in TEXT_SUFFIXES:
                yield f


def check(paths, rules, show_terms=False):
    hits = 0
    for f in files(paths):
        try:
            text = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for n, line in enumerate(text.splitlines(), 1):
            for m in ADDRESS.finditer(line):
                if m.group(0).lower() not in SPEC_ADDRESSES:
                    hits += 1
                    print(f"{f}:{n}: address: {m.group(0)}")
            for term, rx in rules:
                m = rx.search(line)
                if m:
                    hits += 1
                    # By default print no term, so CI logs do not repeat the private list.
                    detail = f"{m.group(0)!r}: {line.strip()[:160]}" if show_terms else "denylisted term"
                    print(f"{f}:{n}: {detail}")
    return hits


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--denylist", help="path to a private denylist file (not in this repository)")
    ap.add_argument("--show-terms", action="store_true", help="print the matched term (local use only)")
    ap.add_argument("paths", nargs="*", default=[str(ROOT)])
    args = ap.parse_args()
    rules = []
    if args.denylist:
        try:
            dl = Path(args.denylist).resolve()
        except OSError as e:
            print(f"cannot read denylist: {e}", file=sys.stderr)
            return 2
        if ROOT in dl.parents:
            print("the denylist must not be inside this repository", file=sys.stderr)
            return 2
        rules = load_denylist(dl)
    hits = check(args.paths, rules, args.show_terms)
    print(f"names_check: {hits} hit(s); {len(rules)} denylist term(s); spec addresses allowed: {len(SPEC_ADDRESSES)}")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
