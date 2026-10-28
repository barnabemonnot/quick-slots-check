"""CHECKED local vector checker and named trap fingerprints.

Candidate ABI and units: see ref.py and README.md. No network access.
"""

import argparse
import copy
from datetime import datetime, timezone
import importlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
TRAP_NAMES = {
    "active_from_genesis": "last configured duration from genesis (including 8 s)",
    "two_eras_only": "two eras only (later changes ignored)",
    "constant_12": "constant 12 after the fork",
    "constant_10": "constant 10 from genesis",
    "virtual_genesis": "virtual genesis without the schedule (wrong before the fork)",
}


def load_candidate(spec):
    module_name, separator, function_name = spec.partition(":")
    function_name = function_name if separator else "evaluate"
    if module_name.endswith(".py"):
        path = Path(module_name).resolve()
        loader = importlib.util.spec_from_file_location("qs_candidate", path)
        if loader is None or loader.loader is None:
            raise ValueError(f"cannot load {path}")
        module = importlib.util.module_from_spec(loader)
        sys.modules["qs_candidate"] = module
        loader.loader.exec_module(module)
    else:
        module = importlib.import_module(module_name)
    function = getattr(module, function_name)
    if not callable(function):
        raise ValueError(f"{spec} is not callable")
    return function, f"{module_name}:{function_name}", module


def requests(data):
    """Use stored expectations. Do not derive them with the candidate."""
    for scenario in data["scenarios"]:
        for case in scenario["cases"]:
            for operation, value, expected in (
                ("slot_start_ms", case["slot"], case["slot_start_time_ms"]),
                ("epoch_at_slot", case["slot"], case["epoch"]),
                ("epoch_start_ms", case["epoch"], case["epoch_start_time_ms"]),
                ("ring_key", case["slot"], case["ring_key"]),
            ):
                yield scenario, case, operation, value, expected
            for probe in case["inverse"]:
                yield scenario, case, "slot_at_time_ms", probe["time_ms"], probe["expected_slot"]


def validate_vectors(data):
    """Check metadata and duplicate fields before candidate execution."""
    if (data["schema_version"], data["genesis_time"], data["slots_per_epoch"],
            data["ring_modulus"]) != (1, 1606824023, 32, 8191):
        raise ValueError("unsupported vector metadata")
    if not data["scenarios"]:
        raise ValueError("empty vector set")
    def integer(x):
        return type(x) is int and 0 <= x <= 2**64 - 1

    for scenario in data["scenarios"]:
        rows = scenario["schedule"]
        if not rows or any(not isinstance(r, list) or len(r) != 2 for r in rows):
            raise ValueError("bad schedule shape")
        if rows[0][0] != 0 or any(not integer(e) or not integer(d) or not d or d % 1000
                                  or e * 32 > 2**64 - 1 for e, d in rows):
            raise ValueError("bad schedule units")
        if any(a[0] >= b[0] for a, b in zip(rows, rows[1:])):
            raise ValueError("bad schedule order")

        def time_at(slot):
            total = data["genesis_time"] * 1000
            for i, (epoch, ms) in enumerate(rows):
                end = rows[i + 1][0] * 32 if i + 1 < len(rows) else slot
                total += max(0, min(slot, end) - epoch * 32) * ms
            return total

        def inverse(t):
            if t < time_at(0):
                raise ValueError("probe before genesis")
            lo, hi = 0, (t - time_at(0)) // min(d for _, d in rows) + 1
            while lo + 1 < hi:
                mid = (lo + hi) // 2
                if time_at(mid) <= t:
                    lo = mid
                else:
                    hi = mid
            return lo

        expected_forks = rows[1:] if len(rows) > 1 else rows
        if len(scenario["forks"]) != len(expected_forks):
            raise ValueError("fork count differs from schedule")
        for fork, (epoch, ms) in zip(scenario["forks"], expected_forks):
            ts = time_at(epoch * 32) // 1000
            iso = datetime.fromtimestamp(ts, timezone.utc).isoformat().replace("+00:00", "Z")
            if fork != dict(epoch=epoch, slot=epoch * 32, time=ts, time_utc=iso, slot_ms=ms):
                raise ValueError("fork metadata differs from schedule")
        first = scenario["forks"][0]
        if any(scenario[key] != first[source] for key, source in
               [("fork_epoch", "epoch"), ("fork_slot", "slot"), ("fork_time", "time"),
                ("fork_time_utc", "time_utc"), ("new_slot_ms", "slot_ms")]):
            raise ValueError("first fork metadata differs from schedule")
        if not scenario["cases"]:
            raise ValueError("empty scenario")
        for case in scenario["cases"]:
            slot = case["slot"]
            if not integer(slot):
                raise ValueError("invalid case slot")
            t = time_at(slot)
            d = next(ms for epoch, ms in reversed(rows) if slot >= epoch * 32)
            probes = [(0, slot), (1, slot), (d // 2, slot), (d - 1, slot), (d, slot + 1)]
            if slot:
                probes.insert(0, (-1, slot - 1))
            if not (
                case["slot_start_time"] * 1000 == t == case["slot_start_time_ms"]
                and case["block_timestamp"] * 1000 == t
                and case["epoch"] == slot // 32
                and case["epoch_start_slot"] == (slot // 32) * 32
                and case["epoch_start_time"] * 1000 == time_at((slot // 32) * 32)
                and case["epoch_start_time_ms"] == time_at((slot // 32) * 32)
                and case["slot_duration_ms"] == d
                and case["relative_to_first_fork"] == slot - first["slot"]
                and case["ring_key"] == (t // 1000) % 8191
                and case["root_storage_index"] == case["ring_key"] + 8191
                and case["inverse"] == [dict(time_ms=t+offset, offset_ms=offset,
                                              expected_slot=expected) for offset, expected in probes]
                and all(inverse(p["time_ms"]) == p["expected_slot"] for p in case["inverse"])
            ):
                raise ValueError(f"inconsistent vector: {scenario['id']}/{case['id']}")


def observe(function, query, genesis_time):
    scenario, _, operation, value, _ = query
    try:
        # Use a fresh list so a candidate cannot change later requests.
        result = function(operation, value, genesis_time=genesis_time,
                          schedule=[tuple(row) for row in scenario["schedule"]])
        return (type(result).__name__, result)
    except Exception as exc:
        return ("exception", f"{type(exc).__name__}: {exc}")


def run(function, label, data, queries, fingerprints):
    observed = [observe(function, q, data["genesis_time"]) for q in queries]
    bad = [i for i, (q, got) in enumerate(zip(queries, observed)) if got != ("int", q[4])]
    cases = sum(len(s["cases"]) for s in data["scenarios"])
    if not bad:
        print(f"CHECKED {label}: PASS ({len(queries)} comparisons, {cases} slot cases, "
              f"{len(data['scenarios'])} schedules)")
        return True, None
    print(f"CHECKED {label}: FAIL ({len(bad)}/{len(queries)} comparisons)")
    detected = next((name for name, signature in fingerprints.items()
                     if observed == signature), None)
    print(f"CHECKED trap detected: {TRAP_NAMES[detected] if detected else 'no exact named signature'}")
    index = bad[0]
    scenario, case, operation, value, expected = queries[index]
    print(f"CHECKED first mismatch: {scenario['id']}, slot={case['slot']}, "
          f"{operation}({value}), expected={expected}, got={observed[index][1]}")
    return False, detected


def self_test(data):
    """Test validation, millisecond floors, second forks and fixture generation."""
    import generate
    import ref

    if data != generate.build():
        raise AssertionError("vectors.json differs from the independent closed-form generator")
    opts = dict(genesis_time=0, schedule=[(0, 12000), (2, 10000), (4, 8000)])
    for slot, time_ms in [(0, 0), (63, 756000), (64, 768000),
                          (65, 778000), (127, 1398000), (128, 1408000),
                          (129, 1416000)]:
        assert ref.slot_start_ms(slot, **opts) == time_ms
        assert ref.slot_at_time_ms(time_ms, **opts) == slot
        if slot:
            assert ref.slot_at_time_ms(time_ms - 1, **opts) == slot - 1
    fractional = dict(genesis_time=0, schedule=[(0, 1250), (1, 750)])
    assert ref.slot_start_ms(32, **fractional) == 40000
    assert ref.slot_at_time_ms(40749, **fractional) == 32
    assert ref.slot_at_time_ms(40750, **fractional) == 33
    bad_calls = [
        lambda: ref.slot_at_time_ms(999, genesis_time=1, schedule=[(0, 12000)]),
        lambda: ref.slot_start_ms(-1, **opts),
        lambda: ref.slot_start_ms(1.0, **opts),
        lambda: ref.slot_start_ms(True, **opts),
        lambda: ref.slot_start_ms(0, genesis_time=0, schedule=[]),
        lambda: ref.slot_start_ms(0, genesis_time=0, schedule=[(1, 12000)]),
        lambda: ref.slot_start_ms(0, genesis_time=0, schedule=[(0, 0)]),
        lambda: ref.slot_start_ms(0, genesis_time=0, schedule=[(0, 12), (0, 10)]),
        lambda: ref.slot_start_ms(0, genesis_time=0, schedule=[(0, 12), (2, 10), (1, 8)]),
        lambda: ref.evaluate("ring_key", 1, **fractional),
    ]
    for call in bad_calls:
        try:
            call()
        except ValueError:
            continue
        raise AssertionError("invalid input was accepted")
    print("CHECKED self-test: PASS (fixture regeneration, three eras, millisecond floors, input errors)")


def contract_test(function, validator, label):
    """Fixed expected values; call the selected candidate, not ref directly."""
    maximum = 2**64 - 1
    base = dict(genesis_time=0, schedule=[(0, 12000), (451, 10000), (457, 8000)])
    arithmetic = [
        ("slot_at_time_ms", 999, dict(genesis_time=1, schedule=[(0, 12000)]), "PRE_GENESIS"),
        ("slot_start_ms", -1, base, "INVALID_INPUT"),
        ("slot_start_ms", True, base, "INVALID_INPUT"),
        ("slot_start_ms", 1.0, base, "INVALID_INPUT"),
        ("slot_start_ms", 0, dict(genesis_time=0, schedule=[]), "INVALID_INPUT"),
        ("slot_start_ms", 0, dict(genesis_time=0, schedule=[(1, 12000)]), "INVALID_INPUT"),
        ("slot_start_ms", 0, dict(genesis_time=0, schedule=[(0, 0)]), "INVALID_INPUT"),
        ("slot_start_ms", 0, dict(genesis_time=0, schedule=[(0, 12000), (0, 10000)]), "INVALID_INPUT"),
        ("slot_start_ms", 0, dict(genesis_time=0, schedule=[(0, 12000), (2, 10000), (1, 8000)]), "INVALID_INPUT"),
        ("slot_start_ms", 0, dict(genesis_time=0, schedule=[0]), "INVALID_INPUT"),
        ("slot_start_ms", 0, dict(genesis_time=0, schedule=[(0, 12000, 1)]), "INVALID_INPUT"),
        ("slot_start_ms", maximum+1, base, "OVERFLOW"),
        ("slot_at_time_ms", maximum+1, base, "OVERFLOW"),
        ("slot_start_ms", maximum, base, "OVERFLOW"),
        ("epoch_start_ms", maximum, base, "OVERFLOW"),
        ("slot_start_ms", 0, dict(genesis_time=maximum, schedule=[(0, 12000)]), "OVERFLOW"),
        ("slot_start_ms", 0, dict(genesis_time=0, schedule=[(0, 12000), (maximum//32+1, 10000)]), "OVERFLOW"),
        ("slot_start_ms", 0, dict(genesis_time=0, schedule=[(0, 12000), (maximum//32, 8000)]), "OVERFLOW"),
        ("slot_start_ms", maximum//12000, dict(genesis_time=0, schedule=[(0, 12000)]), (maximum//12000)*12000),
        ("slot_start_ms", 32, dict(genesis_time=0, schedule=[(0, 1250), (1, 750)]), 40000),
        ("slot_at_time_ms", 40749, dict(genesis_time=0, schedule=[(0, 1250), (1, 750)]), 32),
        ("slot_at_time_ms", 40750, dict(genesis_time=0, schedule=[(0, 1250), (1, 750)]), 33),
        ("ring_key", 1, dict(genesis_time=0, schedule=[(0, 1250)]), "NON_INTEGER_TIMESTAMP"),
        ("unknown", 0, base, "UNKNOWN_OPERATION"),
    ]
    fields = {"HEZE_FORK_EPOCH": 451, "SLOT_DURATION_MS": 12000}
    api = {"SECONDS_PER_SLOT": "12", "SLOT_DURATION_MS": "12000",
           "HEZE_FORK_EPOCH": "451", "SLOT_DURATION_MS_HEZE": "10000",
           "SLOT_DURATION_SCHEDULE": [{"EPOCH": "0", "SLOT_DURATION_MS": "12000"},
                                      {"EPOCH": "451", "SLOT_DURATION_MS": "10000"}]}
    raw = [
        ("normalize_forks", {"legacy_ms": 12000, "forks": [[0, 10000]]}, [[0, 10000]]),
        ("normalize_forks", {"legacy_ms": 12000, "forks": [[0, 10000], [0, 8000]]}, [[0, 8000]]),
        ("normalize_forks", {"legacy_ms": 12000, "forks": [[451, 10000], [451, 8000]]}, [[0, 12000], [451, 8000]]),
        ("normalize_forks", {"legacy_ms": 12000, "forks": [[452, 10000], [451, 8000]]}, "INVALID_INPUT"),
        ("normalize_forks", {"legacy_ms": 12000, "forks": [[maximum, 10000]]}, [[0, 12000]]),
        ("normalize_forks", {"legacy_ms": 12000, "forks": [[451, 12000]]}, [[0, 12000], [451, 12000]]),
        ("normalize_forks", {"legacy_ms": 12000, "forks": [[451, 1250]]}, "INVALID_INPUT"),
        ("config", {"fields": fields}, "MISSING_KEY"),
        ("config", {"fields": {**fields, "SLOT_DURATION_MS_HEZ": 10000}}, "MISSING_KEY"),
        ("config", {"fields": {**fields, "SLOT_DURATION_MS_HEZE": 10000}}, [[0, 12000], [451, 10000]]),
        ("config", {"fields": {**fields, "SLOT_DURATION_MS_HEZE": 10}}, "INVALID_INPUT"),
        ("config", {"fields": {**fields, "SLOT_DURATION_MS_HEZE": 10000, "OLD": 8000}, "aliases": ["OLD"]}, "CONFLICT"),
        ("config", {"fields": {**fields, "SLOT_DURATION_MS_HEZE": 10000, "OLD": 10000}, "aliases": ["OLD"]}, [[0, 12000], [451, 10000]]),
        ("config", {"fields": {**fields, "OLD": 10000}, "aliases": ["OLD"]}, [[0, 12000], [451, 10000]]),
        ("api", api, [[0, 12000], [451, 10000]]),
        ("api", {**api, "SLOT_DURATION_SCHEDULE": [{}]}, "INVALID_INPUT"),
        ("api", {**api, "HEZE_FORK_EPOCH": str(maximum), "SLOT_DURATION_SCHEDULE": api["SLOT_DURATION_SCHEDULE"] + [{"EPOCH": str(maximum), "SLOT_DURATION_MS": "8000"}]}, "INVALID_INPUT"),
        ("api", {**api, "UNRELATED": "allowed", "FUTURE_FORK_EPOCH": "457",
                 "SLOT_DURATION_SCHEDULE": api["SLOT_DURATION_SCHEDULE"] + [{"EPOCH": "457", "SLOT_DURATION_MS": "8000"}]},
                 [[0, 12000], [451, 10000], [457, 8000]]),
        ("api", {**api, "SLOT_DURATION_MS_HEZE": "8000"}, "CONFLICT"),
        ("api", {**api, "SECONDS_PER_SLOT": "10"}, "CONFLICT"),
        ("api", {k: v for k, v in api.items() if k != "SLOT_DURATION_SCHEDULE"}, "MISSING_KEY"),
        ("api", {**api, "SLOT_DURATION_SCHEDULE": api["SLOT_DURATION_SCHEDULE"] * 2}, "INVALID_INPUT"),
        ("api", {**api, "HEZE_FORK_EPOCH": "0", "SLOT_DURATION_SCHEDULE": [{"EPOCH": "0", "SLOT_DURATION_MS": "10000"}]}, [[0, 10000]]),
        ("api", {**api, "SLOT_DURATION_MS": str(maximum+1)}, "OVERFLOW"),
    ]
    if not callable(validator):
        print(f"CHECKED {label} contract: FAIL (missing validate_input)")
        return False
    failures = []
    calls = [(lambda op=op, x=x, options=options: function(op, x, **copy.deepcopy(options)), expected)
             for op, x, options, expected in arithmetic]
    calls += [(lambda kind=kind, x=x: validator(kind, copy.deepcopy(x)), expected)
              for kind, x, expected in raw]
    for index, (call, expected) in enumerate(calls):
        try:
            got = call()
            matched = type(got) is type(expected) and got == expected
        except ValueError as exc:
            got = str(exc)
            matched = isinstance(expected, str) and got == expected
        except Exception as exc:
            got, matched = repr(exc), False
        if not matched:
            failures.append((index, expected, got))
    print(f"CHECKED {label} contract: {'FAIL' if failures else 'PASS'} ({len(calls)} cases)")
    if failures:
        print(f"CHECKED first contract mismatch: {failures[0]}")
    return not failures


def corrupt_fixture_test(data):
    mutations = [
        lambda s: s.update(fork_epoch=s["fork_epoch"]+1),
        lambda s: s.update(fork_slot=s["fork_slot"]+1),
        lambda s: s.update(fork_time=s["fork_time"]+1),
        lambda s: s.update(fork_time_utc="wrong"),
        lambda s: s.update(new_slot_ms=8000),
        lambda s: s["forks"][0].update(time=s["forks"][0]["time"]+1),
        lambda s: s["schedule"].append(s["schedule"][-1]),
        lambda s: s["schedule"][0].__setitem__(1, 0),
        lambda s: s["schedule"][0].append(1),
        lambda s: s["cases"][0]["inverse"][0].update(expected_slot=1),
    ]
    for mutate in mutations:
        broken = copy.deepcopy(data)
        mutate(broken["scenarios"][0])
        try:
            validate_vectors(broken)
        except ValueError:
            continue
        raise AssertionError("corrupt fixture accepted")
    print(f"CHECKED corrupt-fixture tests: PASS ({len(mutations)} rejected)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", nargs="?", default=str(HERE / "ref.py"),
                        help="module[:function] or file.py[:function]; default function: evaluate")
    parser.add_argument("--vectors", type=Path, default=HERE / "vectors.json")
    parser.add_argument("--examples", action="store_true", help="require reference PASS and all named traps FAIL")
    parser.add_argument("--self-test", action="store_true", help="check fixture integrity and the selected candidate input contract")
    args = parser.parse_args()
    try:
        data = json.loads(args.vectors.read_text(encoding="utf-8"))
        validate_vectors(data)
        queries = list(requests(data))
        import traps

        fingerprints = {name: [observe(getattr(traps, name), q, data["genesis_time"])
                               for q in queries] for name in TRAP_NAMES}
        if args.self_test:
            self_test(data)
            corrupt_fixture_test(data)
        if args.examples:
            import ref

            ok, _ = run(ref.evaluate, "ref.py:evaluate", data, queries, fingerprints)
            if args.self_test:
                ok = contract_test(ref.evaluate, ref.validate_input, "ref.py:evaluate") and ok
            for name in TRAP_NAMES:
                passed, detected = run(getattr(traps, name), f"traps.py:{name}",
                                       data, queries, fingerprints)
                ok = ok and not passed and detected == name
            print(f"CHECKED example suite: {'PASS' if ok else 'FAIL'}")
            return 0 if ok else 1
        function, label, module = load_candidate(args.candidate)
        passed, _ = run(function, label, data, queries, fingerprints)
        if args.self_test:
            validator = getattr(function, "validate_input", None) or getattr(module, "validate_input", None)
            passed = contract_test(function, validator, label) and passed
        return 0 if passed else 1
    except Exception as exc:
        print(f"UNVERIFIED checker error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
