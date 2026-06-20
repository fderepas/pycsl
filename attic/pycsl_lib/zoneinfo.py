"""PyCSL mock for Python's zoneinfo module — IANA time zone support."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def available_timezones() -> int:
    """Mock: Get a set containing all the valid keys for IANA time zones available anywhere on the time zone path. This is recalculat..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def reset_tzpath(to: int) -> int:
    """Mock: Sets or resets the time zone search path (:data:`TZPATH`) for the module. When called with no arguments, :data:`TZPATH` ..."""
    return 0
