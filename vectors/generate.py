"""CHECKED vector generator; independent closed forms, no import of ref.py.

Schedules are examples, not announced fork dates.

Run with python3 -B generate.py. Only vectors.json in this folder is written.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

G = 1606824023
OFFSETS = [-8640, -1361, -64, -33, -32, -2, -1, 0, 1, 2, 5, 6,
           31, 32, 33, 359, 360, 7199, 7200, 8190, 8191, 8192,
           8639, 8640, 8641, 10799, 10800, 10801]


def utc(seconds):
    return datetime.fromtimestamp(seconds, timezone.utc).isoformat().replace("+00:00", "Z")


def scenario(epoch, new_seconds, second_epoch=None, genesis_seconds=12):
    f = epoch * 32
    tf = G + genesis_seconds * f
    schedule = [[0, genesis_seconds * 1000]]
    if epoch:
        schedule.append([epoch, new_seconds * 1000])
    else:
        schedule[0][1] = new_seconds * 1000
    changes = [(f, tf, new_seconds)]
    if second_epoch is not None:
        f2 = second_epoch * 32
        t2 = tf + new_seconds * (f2 - f)
        changes.append((f2, t2, 8))
        schedule.append([second_epoch, 8000])

    def time_at(slot):
        # Closed form per era; separate from the reference's era integration.
        if slot < f:
            return G + genesis_seconds * slot
        if second_epoch is not None and slot >= f2:
            return t2 + 8 * (slot - f2)
        return tf + new_seconds * (slot - f)

    def duration_at(slot):
        if slot < f:
            return genesis_seconds
        if second_epoch is not None and slot >= f2:
            return 8
        return new_seconds

    slots = {0, 1, 31, 32}
    offsets = OFFSETS + ([9599, 9600, 9601] if new_seconds == 9 else [])
    for fork_slot, _, _ in changes:
        slots.update(fork_slot + k for k in offsets if fork_slot + k >= 0)
    cases = []
    for slot in sorted(slots):
        t = time_at(slot)
        duration_ms = duration_at(slot) * 1000
        epoch_at_slot = slot // 32
        epoch_start = time_at(epoch_at_slot * 32)
        # The right boundary belongs to the next slot. All other probes are inside.
        probes = [(0, slot), (1, slot), (duration_ms // 2, slot),
                  (duration_ms - 1, slot), (duration_ms, slot + 1)]
        if slot:
            probes.insert(0, (-1, slot - 1))
        cases.append({
            "id": f"slot-{slot}", "arithmetic_status": "CHECKED",
            "network_status": "INFERRED", "slot": slot,
            "relative_to_first_fork": slot - f,
            "slot_duration_ms": duration_ms,
            "slot_start_time": t, "slot_start_time_ms": t * 1000,
            "epoch": epoch_at_slot, "epoch_start_slot": epoch_at_slot * 32,
            "epoch_start_time": epoch_start, "epoch_start_time_ms": epoch_start * 1000,
            "block_timestamp": t, "ring_key": t % 8191,
            "root_storage_index": t % 8191 + 8191,
            "inverse": [{"time_ms": t * 1000 + offset, "offset_ms": offset,
                         "expected_slot": expected} for offset, expected in probes],
        })
    label = f"epoch-{epoch}-12-to-{new_seconds}s"
    if second_epoch is not None:
        label += f"-then-8s-at-{second_epoch}"
    return {
        "id": label, "schedule": schedule,
        "fork_epoch": epoch, "fork_slot": f,
        "fork_time": tf, "fork_time_utc": utc(tf),
        "new_slot_ms": new_seconds * 1000,
        "forks": [{"epoch": fs // 32, "slot": fs, "time": ts,
                   "time_utc": utc(ts), "slot_ms": d * 1000}
                  for fs, ts, d in changes],
        "cases": cases,
    }


def build():
    primary = [scenario(epoch, d) for epoch in (500000, 582000, 500001, 500002, 500003, 500004, 451, 452) for d in (10, 8)]
    # Published devnet-3 schedule SHAPE only. Keep the suite's example genesis:
    # MIN_GENESIS_TIME in a config is not an observed network genesis timestamp.
    devnet9 = scenario(5, 9)
    devnet9["schedule_source"] = "A published public devnet configuration: SLOT_DURATION_MS 12000, SLOT_DURATION_MS_HEZE 9000, HEZE_FORK_EPOCH 5 (shape only)"
    devnet9["genesis_status"] = "Example suite genesis, not the live devnet genesis"
    return {
        "schema_version": 1, "genesis_time": G, "slots_per_epoch": 32,
        "ring_modulus": 8191,
        "arithmetic_status": "CHECKED", "network_status": "INFERRED",
        "fork_dates_status": "INFERRED",
        "scope": "Example schedules; not announced mainnet fork dates.",
        "units": {"genesis_time": "Unix seconds", "time": "Unix seconds",
                  "time_ms": "Unix milliseconds", "schedule": "[epoch, slot_ms]"},
        "sources": ["spec/R01-slot-time-formula.md",
                    "spec/R04-4788-migration.md",
                    "https://eips.ethereum.org/EIPS/eip-8198",
                    "https://eips.ethereum.org/EIPS/eip-4788#beacon-roots-contract"],
        "offsets": OFFSETS,
        "scenarios": primary + [scenario(500000, 10, second_epoch=500002),
                                scenario(451, 10, second_epoch=457),
                                scenario(451, 12), scenario(0, 10, genesis_seconds=10),
                                scenario(0, 8, genesis_seconds=8), devnet9],
    }


if __name__ == "__main__":
    destination = Path(__file__).with_name("vectors.json")
    data = build()
    destination.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    count = sum(len(s["cases"]) for s in data["scenarios"])
    print(f"CHECKED wrote {len(data['scenarios'])} scenarios, {count} slot cases")
