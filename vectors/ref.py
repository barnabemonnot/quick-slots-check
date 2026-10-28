"""CHECKED local reference for spec gap R1; network behaviour is INFERRED.

Use integer Unix milliseconds. Schedule entries are (epoch, slot_ms).
Epochs default to 32 slots; an explicit slots_per_epoch supports other presets.
A new duration starts at the named epoch.
"""

SLOTS_PER_EPOCH = 32
HISTORY_BUFFER_LENGTH = 8191
MAX_UINT64 = 2**64 - 1

from conformance import validate_input


def _uint(value, name):
    if type(value) is not int or value < 0:
        raise ValueError("INVALID_INPUT")
    if value > MAX_UINT64:
        raise ValueError("OVERFLOW")
    return value


def _eras(genesis_time, schedule, slots_per_epoch=SLOTS_PER_EPOCH):
    """Integrate all earlier durations to find each era's time anchor."""
    _uint(genesis_time, "genesis_time")
    _uint(slots_per_epoch, "slots_per_epoch")
    if slots_per_epoch == 0:
        raise ValueError("INVALID_INPUT")
    if not isinstance(schedule, (list, tuple)) or not schedule:
        raise ValueError("INVALID_INPUT")
    eras = []
    for entry in schedule:
        if not isinstance(entry, (list, tuple)) or len(entry) != 2:
            raise ValueError("INVALID_INPUT")
        epoch, duration = entry
        _uint(epoch, "epoch")
        _uint(duration, "slot_ms")
        if duration == 0:
            raise ValueError("INVALID_INPUT")
        slot = _uint(epoch * slots_per_epoch, "start_slot")
        if not eras:
            if epoch != 0:
                raise ValueError("INVALID_INPUT")
            time_ms = _uint(genesis_time * 1000, "genesis_ms")
        else:
            prev_slot, prev_time, prev_duration = eras[-1]
            if slot <= prev_slot:
                raise ValueError("INVALID_INPUT")
            time_ms = _uint(prev_time + (slot - prev_slot) * prev_duration, "anchor_ms")
        eras.append((slot, time_ms, duration))
    return eras


def slot_start_ms(slot, *, genesis_time, schedule, slots_per_epoch=SLOTS_PER_EPOCH):
    _uint(slot, "slot")
    for start_slot, time_ms, duration in reversed(_eras(genesis_time, schedule, slots_per_epoch)):
        if slot >= start_slot:
            return _uint(time_ms + (slot - start_slot) * duration, "time_ms")
    raise AssertionError("missing genesis era")


def slot_at_time_ms(time_ms, *, genesis_time, schedule, slots_per_epoch=SLOTS_PER_EPOCH):
    _uint(time_ms, "time_ms")
    for start_slot, start_ms, duration in reversed(_eras(genesis_time, schedule, slots_per_epoch)):
        if time_ms >= start_ms:
            return _uint(start_slot + (time_ms - start_ms) // duration, "slot")
    raise ValueError("PRE_GENESIS")


def evaluate(operation, value, *, genesis_time, schedule, slots_per_epoch=SLOTS_PER_EPOCH):
    """Candidate ABI: evaluate(operation, int, *, genesis_time, schedule) -> int.

    genesis_time is in seconds; time inputs and outputs use milliseconds.
    ring_key is the timestamp storage index, not the timestamp lookup input.
    Optional slots_per_epoch is a positive uint64 preset value, defaulting to 32.
    """
    options = dict(genesis_time=genesis_time, schedule=schedule, slots_per_epoch=slots_per_epoch)
    _uint(slots_per_epoch, "slots_per_epoch")
    if slots_per_epoch == 0:
        raise ValueError("INVALID_INPUT")
    _uint(value, "value")
    if operation == "slot_start_ms":
        return slot_start_ms(value, **options)
    if operation == "slot_at_time_ms":
        return slot_at_time_ms(value, **options)
    if operation == "epoch_at_slot":
        _eras(genesis_time, schedule, slots_per_epoch)
        return value // slots_per_epoch
    if operation == "epoch_start_ms":
        return slot_start_ms(_uint(value * slots_per_epoch, "slot"), **options)
    if operation == "ring_key":
        time_ms = slot_start_ms(value, **options)
        if time_ms % 1000:
            raise ValueError("NON_INTEGER_TIMESTAMP")
        return (time_ms // 1000) % HISTORY_BUFFER_LENGTH
    raise ValueError("UNKNOWN_OPERATION")
