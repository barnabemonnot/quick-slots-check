"""Proposed R2/R3 validation policy. This is not a client implementation.

Raw fork entries use consensus fork order. API rows are already normalized.
Declared aliases in these tests do not establish an upstream alias policy.
"""

MAX = 2**64 - 1


def uint(value, *, decimal=False):
    if decimal:
        if not isinstance(value, str) or not value.isascii() or not value.isdecimal():
            raise ValueError("INVALID_INPUT")
        if str(int(value)) != value:
            raise ValueError("INVALID_INPUT")
        value = int(value)
    if type(value) is not int or value < 0:
        raise ValueError("INVALID_INPUT")
    if value > MAX:
        raise ValueError("OVERFLOW")
    return value


def duration(value, *, decimal=False):
    value = uint(value, decimal=decimal)
    if value == 0 or value % 1000:
        raise ValueError("INVALID_INPUT")
    return value


def epoch_size(value):
    value = uint(value)
    if value == 0:
        raise ValueError("INVALID_INPUT")
    return value


def normalized(rows, *, slots_per_epoch=32):
    slots_per_epoch = epoch_size(slots_per_epoch)
    if not isinstance(rows, (list, tuple)) or not rows:
        raise ValueError("INVALID_INPUT")
    result = []
    for row in rows:
        if not isinstance(row, (list, tuple)) or len(row) != 2:
            raise ValueError("INVALID_INPUT")
        epoch, ms = uint(row[0]), duration(row[1])
        if epoch == MAX:
            raise ValueError("INVALID_INPUT")
        uint(epoch * slots_per_epoch)
        if (not result and epoch != 0) or (result and epoch <= result[-1][0]):
            raise ValueError("INVALID_INPUT")
        result.append([epoch, ms])
    anchor = 0
    for (epoch, ms), (next_epoch, _) in zip(result, result[1:]):
        anchor = uint(anchor + (next_epoch - epoch) * slots_per_epoch * ms)
    return result


def _validate_input(kind, value, slots_per_epoch):
    """Return list[list[int]] or raise ValueError with a documented code."""
    if kind == "normalize_forks":
        rows = [[0, duration(value["legacy_ms"])]]
        last_epoch = 0
        for entry in value["forks"]:
            if not isinstance(entry, (list, tuple)) or len(entry) != 2:
                raise ValueError("INVALID_INPUT")
            epoch, ms = uint(entry[0]), duration(entry[1])
            if epoch == MAX:
                continue
            if epoch < last_epoch:
                raise ValueError("INVALID_INPUT")
            if epoch == rows[-1][0]:
                rows[-1][1] = ms
            else:
                rows.append([epoch, ms])
            last_epoch = epoch
        return normalized(rows, slots_per_epoch=slots_per_epoch)
    if kind == "config":
        fields = value["fields"]  # Check raw supplied fields before any defaults.
        if "SLOTS_PER_EPOCH" in fields and epoch_size(fields["SLOTS_PER_EPOCH"]) != slots_per_epoch:
            raise ValueError("CONFLICT")
        if any(key not in fields for key in ("HEZE_FORK_EPOCH", "SLOT_DURATION_MS")):
            raise ValueError("MISSING_KEY")
        epoch = uint(fields["HEZE_FORK_EPOCH"])
        legacy = duration(fields["SLOT_DURATION_MS"])
        canonical = "SLOT_DURATION_MS_HEZE"
        names = [canonical] + value.get("aliases", [])
        supplied = [duration(fields[name]) for name in names if name in fields]
        if epoch != MAX and not supplied:
            raise ValueError("MISSING_KEY")
        if supplied and any(ms != supplied[0] for ms in supplied):
            raise ValueError("CONFLICT")
        return validate_input("normalize_forks", {"legacy_ms": legacy,
                              "forks": [[epoch, supplied[0]]] if supplied else []},
                              slots_per_epoch=slots_per_epoch)
    if kind == "api":
        if "SLOTS_PER_EPOCH" in value and epoch_size(uint(value["SLOTS_PER_EPOCH"], decimal=True)) != slots_per_epoch:
            raise ValueError("CONFLICT")
        if any(key not in value for key in ("SLOT_DURATION_MS", "SECONDS_PER_SLOT")):
            raise ValueError("MISSING_KEY")
        legacy = duration(value["SLOT_DURATION_MS"], decimal=True)
        seconds = uint(value["SECONDS_PER_SLOT"], decimal=True)
        if uint(seconds * 1000) != legacy:
            raise ValueError("CONFLICT")
        if "SLOT_DURATION_SCHEDULE" not in value:
            raise ValueError("MISSING_KEY")
        rows = normalized([[uint(row["EPOCH"], decimal=True),
                            duration(row["SLOT_DURATION_MS"], decimal=True)]
                           for row in value["SLOT_DURATION_SCHEDULE"]],
                          slots_per_epoch=slots_per_epoch)
        if "HEZE_FORK_EPOCH" in value:
            epoch = uint(value["HEZE_FORK_EPOCH"], decimal=True)
            if epoch != MAX:
                if "SLOT_DURATION_MS_HEZE" not in value:
                    raise ValueError("MISSING_KEY")
                ms = duration(value["SLOT_DURATION_MS_HEZE"], decimal=True)
                if [epoch, ms] not in rows:
                    raise ValueError("CONFLICT")
        return rows  # Unrelated fields and unknown future fork names are allowed.
    raise ValueError("UNKNOWN_OPERATION")


def validate_input(kind, value, *, slots_per_epoch=32):
    try:
        return _validate_input(kind, value, epoch_size(slots_per_epoch))
    except (KeyError, TypeError, IndexError, AttributeError):
        raise ValueError("INVALID_INPUT") from None
