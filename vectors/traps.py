"""CHECKED examples of wrong clock formulas. Local arithmetic only.

These functions have the candidate ABI from ref.py. They are not fixes.
"""


def _evaluate(operation, value, genesis_time, duration_ms, anchor_ms):
    if operation == "slot_start_ms":
        return anchor_ms + value * duration_ms
    if operation == "slot_at_time_ms":
        return (value - anchor_ms) // duration_ms
    if operation == "epoch_at_slot":
        return value // 32
    if operation == "epoch_start_ms":
        return anchor_ms + value * 32 * duration_ms
    if operation == "ring_key":
        return ((anchor_ms + value * duration_ms) // 1000) % 8191
    raise ValueError(operation)


def constant_12(operation, value, *, genesis_time, schedule):
    """Trap: constant 12 after the fork."""
    return _evaluate(operation, value, genesis_time, 12000, genesis_time * 1000)


def constant_10(operation, value, *, genesis_time, schedule):
    """Trap: constant 10 from genesis, including in the 8 s scenarios."""
    return _evaluate(operation, value, genesis_time, 10000, genesis_time * 1000)


def virtual_genesis(operation, value, *, genesis_time, schedule):
    """Trap: latest virtual genesis without the schedule; wrong in history."""
    start_ms = genesis_time * 1000
    previous_epoch, previous_ms = schedule[0]
    for epoch, duration_ms in schedule[1:]:
        start_ms += (epoch - previous_epoch) * 32 * previous_ms
        previous_epoch, previous_ms = epoch, duration_ms
    anchor_ms = start_ms - previous_epoch * 32 * previous_ms
    return _evaluate(operation, value, genesis_time, previous_ms, anchor_ms)


def active_from_genesis(operation, value, *, genesis_time, schedule):
    """Trap: use the last configured duration over all history, including 8 s."""
    return _evaluate(operation, value, genesis_time, schedule[-1][1], genesis_time * 1000)


def two_eras_only(operation, value, *, genesis_time, schedule):
    """Trap: ignore every duration change after the first one."""
    import ref
    return ref.evaluate(operation, value, genesis_time=genesis_time, schedule=schedule[:2])
