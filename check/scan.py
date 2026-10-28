#!/usr/bin/env python3
"""Find code that may assume 12-second slots.

  python3 check/scan.py <path> [<path> ...]     # print file:line: RULE [class] doc -- code
  python3 check/scan.py --json <path>           # one JSON object per hit
  python3 check/scan.py --rules                 # list rules and the docs they map to
  python3 check/scan.py --self-test             # run the synthetic fixtures in check/fixtures/

A hit is a lead, not a finding. Half of the top hits of an earlier text census were code that does not run. Read the
path that runs, then use the class doc and the vectors. Read-only: the scanner opens files and prints; it writes
nothing and uses no network.

Languages: Solidity (*.sol, the most complete rule set), Go, Rust, Python, TypeScript and JavaScript. The generic
rules are conservative: most need a slot, epoch, genesis or beacon word within three lines.

Exit status: 0 = scan finished (hits or not); 1 = --fail-on-hit and at least one hit, or a self-test failure;
2 = usage error.
"""
import argparse
import bisect
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOL = {".sol"}
GEN = {".go", ".rs", ".py", ".ts", ".tsx", ".js", ".mjs", ".cjs"}
SKIP_DIRS = {".git", "node_modules", "vendor", "target", "dist", "build", "__pycache__", ".venv", "venv", "lib/forge-std"}


def rx(p, flags=re.I):
    return re.compile(p, flags)


# --- Comment stripping. Line positions are kept, so hits map to real lines. ---
C_TOKEN = re.compile(r'''"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*'|`(?:\\.|[^`\\])*`|//[^\n]*|/\*[\s\S]*?\*/''')
PY_TOKEN = re.compile(r'''"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*'|#[^\n]*''')


def _blank(m):
    s = m.group(0)
    if s.startswith(("//", "/*", "#")):
        return re.sub(r"[^\n]", " ", s)
    return s


def strip_comments(src, suffix):
    tok = PY_TOKEN if suffix == ".py" else C_TOKEN
    return tok.sub(_blank, src)


SLOTCTX = rx(r"slot|epoch|genesis|beacon")
BLOCKCTX = rx(r"block")
WINDOW = rx(r"block\s*\.\s*number|\b(?:256|8191|8192)\b|window|[Aa]ge\b|[Ee]xpir|[Dd]eadline")
VERBS = ("reward|rate|borrow|supply|interest|emission|token|mint|distribution|accrual|profit|yield|bonus|dividend|"
         "debt|fee|income|payout|allocation|inflation")

# Each rule: id, languages, regex, context check, class, doc, short note.
# Context checks: None, "slot" (slot/epoch/genesis/beacon within 3 lines), "block" (the word block within 3 lines),
# "gov" (block within 20 lines), "window2935" (window words within 12 lines), "notimestamp" (skip lines that use
# block.timestamp).
RULES = [
    # Solidity rules, ported from the census patterns.
    ("SOL-BLOCKS-PER-YEAR", SOL, rx(r"(?<![\w])(?:2102400|2372500|2628000|2632500|2336000|2252571|2254114|2425846|2404800|10512000|5256000|4204800)(?![\w])"),
     "notimestamp", "ON6", "classes/ON6-per-block-rates.md", "blocks-per-year constant"),
    ("SOL-BLOCKS-PER-DAY", SOL, rx(r"(?<![\w])(?:5760|6570|7200|6500|6646|6400|19710|19636)(?![\w])"),
     "block+notimestamp", "ON6", "classes/ON6-per-block-rates.md", "blocks-per-day constant"),
    ("SOL-BLOCKS-PER-WEEK", SOL, rx(r"(?<![\w])(?:40320|45500|50400|44800)(?![\w])"),
     "block+notimestamp", "ON4", "classes/ON4-block-count-security-windows.md", "blocks-per-week constant"),
    ("SOL-PER-BLOCK-RATE", SOL, rx(r"\b\w*(?:" + VERBS + r")PerBlock\w*\b"),
     "notimestamp", "ON6", "classes/ON6-per-block-rates.md", "per-block rate"),
    ("SOL-PER-BLOCK-IDENT", SOL, rx(r"\b[A-Za-z_]\w*PerBlock\w*\b"),
     "notimestamp", "ON6", "classes/ON6-per-block-rates.md", "per-block identifier"),
    ("SOL-BLOCKS-PER-X", SOL, rx(r"\b(?:blocks?_?per_?(?:year|day|week|month|hour|epoch)|(?:year|day|week|month|hour)ly?_?blocks?)\w*\b"),
     "notimestamp", "ON6", "classes/ON6-per-block-rates.md", "blocks-per-period identifier"),
    ("SOL-GOV-BLOCKS", SOL, re.compile(r"\b(?:votingPeriod|votingDelay|VOTING_PERIOD|VOTING_DELAY|proposalEta|timelockDelay)\b"),
     "gov+notimestamp", "ON5", "classes/ON5-block-count-governance-windows.md", "governance window"),
    ("SOL-SLOT-EPOCH-CONST", SOL, rx(r"\b(?:seconds?_per_slot|secondsperslot|slot_duration|slotduration|slots?_per_epoch|slotsperepoch|seconds?_per_epoch|secondsperepoch|genesis_?time|beacon_?genesis)\b"),
     "notimestamp", "ON1", "classes/ON1-oracle-epoch-clocks.md", "slot or epoch constant"),
    ("SOL-BLOCK-TIME", SOL, rx(r"\b(?:seconds?_per_block|secondsperblock|block_?time|average_?block_?time|avg_?block_?time|block_?period|block_?interval|time_?per_block)\b"),
     "notimestamp", "ON4", "classes/ON4-block-count-security-windows.md", "block-time assumption"),
    ("SOL-BLOCK-DEADLINE", SOL, re.compile(r"block\s*\.\s*number\s*[+\-]\s*(?:[4-9][0-9]|[0-9]{3,})(?!\d)|(?<!\d)(?:[4-9][0-9]|[0-9]{3,})\s*\+\s*block\s*\.\s*number"),
     "notimestamp", "ON4", "classes/ON4-block-count-security-windows.md", "block-number deadline"),
    ("SOL-TIMESTAMP-DIV-12", SOL, rx(r"(?:timestamp|time)\s*\)?\s*(?:-[^;/]{0,60})?/\s*12\b"),
     "notimestamp", "ON1", "classes/ON1-oracle-epoch-clocks.md", "time divided by 12"),
    ("SOL-4788", SOL, rx(r"0x000f3df6d732807ef1319fb7b8bb8522d0beac02|\b\w*BEACON_ROOTS\w*\b|\b(?:getBeaconRoot|getParentBeaconBlockRoot|beaconRootsAddress|beaconRootsContract)\b"),
     None, "ON2", "classes/ON2-4788-computed-timestamp.md", "EIP-4788 beacon roots use"),
    ("SOL-2935", SOL, rx(r"0x0000f90827f1c53a10cb7a02335b175320002935|\bblockhash\s*\("),
     "window2935", "R6", "spec/R06-2935-history-window.md", "block-hash history window"),
    ("SOL-7002-7251", SOL, rx(r"0x00000961ef480eb55e80d19ad83579a64c007002|0x0000bbddc7ce488642fb579f8b00f3a590007251"),
     None, "R7", "spec/R07-request-fee-dynamics.md", "EIP-7002/7251 request contract"),
    ("SOL-TWELVE-ARITH", SOL, rx(r"\*\s*12\b|/\s*12\b|\b12\s*(?:seconds\b|\*)|\b(?:384|7200|50400|216000)\b"),
     "slot", "ON7", "classes/ON7-fixed-12s-grids.md", "12 s arithmetic"),
    ("SOL-BLOCK-WINDOW", SOL, re.compile(r"\b[A-Za-z_]\w*(?:Blocks|_BLOCKS)\w*\b|\b(?:periodInBlocks|lockBlocks|delayBlocks|expiryBlock|expirationBlock|deadlineBlock|endBlock)\b|\bstartBlock\s*\+"),
     "notimestamp-only", "ON4", "classes/ON4-block-count-security-windows.md", "window counted in blocks"),
    ("SOL-FOLDED-EPOCH-PRICE", SOL, re.compile(r"\b4444444444444445\b|\b384e18\s*/\s*86400\b|\b384\s*\*\s*1e18\s*/\s*86400\b"),
     None, "ON7", "classes/ON7-fixed-12s-grids.md", "folded per-epoch price (384 s epoch per day)"),
    # Generic rules for offchain code (also run on Solidity where they make sense).
    ("GEN-GENESIS-PLUS-12", SOL | GEN, rx(r"genesis\w*\s*(?:\)|\.\w+(?:\(\))?)?\s*\+\s*\(?\s*[\w.()\[\]]*slot[\w.()\[\]]*\s*\)?\s*\*\s*\(?\s*(?:12|12000|12_000)\b|genesis\w*\s*(?:\)|\.\w+(?:\(\))?)?\s*\+\s*\(?\s*(?:12|12000|12_000)\s*\*\s*\(?\s*[\w.()\[\]]*slot|\b(?:12|12000|12_000)\s*\*\s*\(?\s*[\w.()\[\]]*slot[\w.()\[\]]*\s*\)?\s*\+\s*[\w.()]*genesis"),
     None, "R1", "spec/R01-slot-time-formula.md", "genesis + 12*slot (single-duration clock)"),
    ("GEN-DIV-12-FROM-GENESIS", SOL | GEN, rx(r"-\s*[\w.()\[\]]*genesis[\w.()\[\]]*\s*\)\s*(?:/{1,2}|\.(?:div|Div|checked_div)\s*\(|\.saturating_div\s*\()\s*\(?\s*(?:12|12000|12_000)\b"),
     None, "R1", "spec/R01-slot-time-formula.md", "(t - genesis) / 12 (single-duration clock)"),
    ("GEN-SLOT-DURATION-12", GEN, rx(r"\b(?:SECONDS_PER_SLOT|SecondsPerSlot|seconds_per_slot|secondsPerSlot|SLOT_DURATION(?:_MS|_SECONDS)?|SlotDuration(?:Ms|Millis)?|slot_duration(?:_ms|_secs)?|slotDuration(?:Ms)?|SLOT_TIME|slot_time)\b\s*(?::\s*[\w:<>]+\s*)?(?::=|=|:)\s*(?:u64|uint64|int|Number|time\.Duration)?\s*\(?\s*(?:12|12000|12_000)(?:\s*\*\s*time\.(?:Second|Millisecond))?\b"),
     None, "OFF1", "classes/OFF1-duty-clients-dvt.md", "slot duration fixed at 12 s"),
    ("GEN-DURATION-12S", GEN, rx(r"\b12\s*\*\s*time\.Second\b|\btime\.Second\s*\*\s*12\b|Duration::from_secs\s*\(\s*12\s*\)|Duration::from_millis\s*\(\s*12_?000\s*\)|timedelta\s*\(\s*seconds\s*=\s*12\s*\)|\b12_?000\s*\*\s*time\.Millisecond\b"),
     "slot", "OFF5", "classes/OFF5-pbs.md", "12 s duration near slot code"),
    ("GEN-SLOT-DURATION-10", SOL | GEN, rx(r"\b(?:SECONDS_PER_SLOT|SecondsPerSlot|seconds_per_slot|secondsPerSlot|SLOT_DURATION(?:_MS|_SECONDS)?|SlotDuration(?:Ms|Millis)?|slot_duration(?:_ms|_secs)?|slotDuration(?:Ms)?)\b\s*(?::\s*[\w:<>]+\s*)?(?::=|=|:)\s*(?:u64|uint64|uint256|int|Number)?\s*\(?\s*(?:10|10000|10_000)\b"),
     None, "W1", "checklists/wrong-fixes.md#w1", "slot duration set to 10: check that genesis is not still the anchor"),
    ("GEN-OVERRIDE-FLAG", SOL | GEN, rx(r"slot[-_]?duration[-_]?override|SLOT_DURATION_OVERRIDE"),
     None, "W1", "checklists/wrong-fixes.md#w1", "one-value slot-duration override"),
    ("GEN-EPOCH-384", GEN, rx(r"(?<![\w.])384(?:_?000)?(?![\w.])"),
     "slot", "OFF7", "classes/OFF7-monitoring-ui.md", "384 s epoch"),
    ("GEN-SLOTS-PER-DAY-7200", GEN, rx(r"(?<![\w.])7_?200(?![\w.])"),
     "slot", "OFF7", "classes/OFF7-monitoring-ui.md", "7,200 slots per day"),
    ("GEN-MAINNET-GENESIS", SOL | GEN, re.compile(r"(?<!\d)1606824023(?:000)?(?!\d)"),
     None, "R1", "spec/R01-slot-time-formula.md", "mainnet genesis literal: check how it is combined"),
    ("GEN-SINGLE-DURATION-API", GEN, re.compile(r"\b(?:get_slot_duration|slot_duration|SlotDuration|SlotDurationMillis|SecondsPerSlot|seconds_per_slot|secondsPerSlot)\s*\(\s*\)"),
     None, "OFF6", "classes/OFF6-shared-libraries.md", "single-duration API call"),
    ("GEN-FORK-NAME-EQ", GEN, re.compile(r"==\s*(?:&\s*)?ForkName::\w+|ForkName::\w+\s*==|==\s*(?:spec\.)?ForkName\.\w+|ForkName\.\w+\s*==|==\s*version\.(?:Gloas|Heze|Fulu|Electra)\b"),
     None, "W9", "checklists/wrong-fixes.md#w9", "exact fork-name gate"),
    ("GEN-4788-KEY", GEN, rx(r"%\s*8191\b|\bBEACON_ROOTS\w*\b|0x000f3df6d732807ef1319fb7b8bb8522d0beac02"),
     None, "ON2", "classes/ON2-4788-computed-timestamp.md", "EIP-4788 key arithmetic"),
]


def _context_ok(ctx, lines, i, line, cat_is_baseline=True):
    if ctx is None:
        return True
    near = "\n".join(lines[max(0, i - 3):i + 4])
    for part in ctx.split("+"):
        if part == "slot" and not SLOTCTX.search(near):
            return False
        if part == "block" and not BLOCKCTX.search(near):
            return False
        if part == "gov" and not re.search(r"block\s*\.\s*number|[Bb]lock", "\n".join(lines[max(0, i - 20):i + 21])):
            return False
        if part == "window2935" and "2935" not in line and not WINDOW.search("\n".join(lines[max(0, i - 12):i + 13])):
            return False
        if part == "notimestamp" and re.search(r"block\s*\.\s*timestamp", line):
            return False
        if part == "notimestamp-only" and re.search(r"block\s*\.\s*timestamp", line) and not re.search(r"block\s*\.\s*number", line):
            return False
    return True


def scan_text(src, suffix):
    clean = strip_comments(src, suffix)
    lines = clean.split("\n")
    raw_lines = src.split("\n")
    starts = [0]
    for line in lines:
        starts.append(starts[-1] + len(line) + 1)
    hits = []
    for rid, langs, rule, ctx, cls, doc, note in RULES:
        if suffix not in langs:
            continue
        seen = set()
        for m in rule.finditer(clean):
            i = bisect.bisect_right(starts, m.start()) - 1
            if i in seen:
                continue
            if rid == "SOL-TWELVE-ARITH" and m.group(0) in ("7200", "50400", "216000") and not BLOCKCTX.search("\n".join(lines[max(0, i - 3):i + 4])):
                continue
            if not _context_ok(ctx, raw_lines if len(raw_lines) == len(lines) else lines, i, lines[i]):
                continue
            seen.add(i)
            hits.append({"line": i + 1, "rule": rid, "class": cls, "doc": doc, "note": note,
                         "match": m.group(0)[:120], "code": raw_lines[i].strip()[:200]})
    return sorted(hits, key=lambda h: (h["line"], h["rule"]))


def iter_files(paths):
    for p in paths:
        p = Path(p)
        if p.is_file():
            if p.suffix in SOL | GEN:
                yield p
            continue
        for f in sorted(p.rglob("*")):
            if not f.is_file() or f.suffix not in SOL | GEN:
                continue
            rel = f.relative_to(p).as_posix()
            if any(part in SKIP_DIRS for part in f.relative_to(p).parts) or any(rel.startswith(d + "/") for d in SKIP_DIRS):
                continue
            yield f


def scan_paths(paths):
    for f in iter_files(paths):
        try:
            src = f.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"{f}: cannot read: {e}", file=sys.stderr)
            continue
        for h in scan_text(src, f.suffix):
            yield f, h


def self_test():
    fixtures = HERE / "fixtures"
    expected = json.loads((fixtures / "expected.json").read_text(encoding="utf-8"))
    got = {}
    for f, h in scan_paths([fixtures]):
        got.setdefault(f.relative_to(fixtures).as_posix(), set()).add((h["line"], h["rule"]))
    ok = True
    for name, rows in expected.items():
        want = {(r[0], r[1]) for r in rows}
        have = got.get(name, set())
        for miss in sorted(want - have):
            ok = False
            print(f"MISSING {name}:{miss[0]}: {miss[1]}")
        for extra in sorted(have - want):
            ok = False
            print(f"UNEXPECTED {name}:{extra[0]}: {extra[1]}")
    for name in sorted(set(got) - set(expected)):
        ok = False
        print(f"UNEXPECTED FILE {name}: {sorted(got[name])}")
    rule_ids = {r[0] for r in RULES}
    covered = {r[1] for rows in expected.values() for r in rows}
    missing_rules = sorted(rule_ids - covered)
    if missing_rules:
        ok = False
        print("RULES WITHOUT A POSITIVE FIXTURE: " + ", ".join(missing_rules))
    for rid, _, _, _, _, doc, _ in RULES:
        if not (ROOT / doc.split("#")[0]).is_file():
            ok = False
            print(f"MISSING DOC for {rid}: {doc}")
    n = sum(len(v) for v in expected.values())
    print(f"scan self-test: {'PASS' if ok else 'FAIL'} ({n} expected hits, {len(expected)} fixture files, {len(RULES)} rules)")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--json", action="store_true", help="one JSON object per hit")
    ap.add_argument("--rules", action="store_true", help="list rules")
    ap.add_argument("--self-test", action="store_true", help="run the synthetic fixtures")
    ap.add_argument("--fail-on-hit", action="store_true", help="exit 1 if anything is found")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if args.rules:
        print("| Rule | Languages | Class | Doc | What it flags |")
        print("|---|---|---|---|---|")
        for rid, langs, _, _, cls, doc, note in RULES:
            lang = "Solidity" if langs == SOL else ("Solidity, generic" if SOL <= langs else "generic")
            print(f"| {rid} | {lang} | {cls} | {doc} | {note} |")
        return 0
    if not args.paths:
        ap.print_usage(sys.stderr)
        return 2
    n = 0
    for f, h in scan_paths(args.paths):
        n += 1
        if args.json:
            print(json.dumps({"file": str(f), **h}))
        else:
            print(f"{f}:{h['line']}: {h['rule']} [{h['class']}] {h['doc']} -- {h['code']}")
    if not args.json:
        print(f"scan: {n} hit(s). Each hit is a lead: read the path that runs.", file=sys.stderr)
    return 1 if (args.fail_on_hit and n) else 0


if __name__ == "__main__":
    sys.exit(main())
