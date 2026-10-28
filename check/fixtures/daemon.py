"""Synthetic fixture for check/scan.py. Not taken from any project."""
from datetime import timedelta

GENESIS_TIME = 1606824023
SLOT_DURATION = 10  # wrong fix: duration changed, genesis kept


def slot_at(t):
    return (t - GENESIS_TIME) // 12


def beacon_root_key(slot):
    return (GENESIS_TIME + 12 * slot) % 8191


def slots_per_day(slot):
    return 7200


TICK = timedelta(seconds=12)  # one slot
