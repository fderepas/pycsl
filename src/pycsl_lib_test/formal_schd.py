# Formal tests for pycsl_lib/schd — sched module
# Class through imports loses precision.


#@ requires events >= 0
#@ ensures \result == events + 1
def test_enter_increments(events: int) -> int:
    """Scheduling event increments count."""
    return events + 1


#@ requires events > 0
#@ ensures \result == events - 1
def test_cancel_decrements(events: int) -> int:
    """Cancelling event decrements count."""
    return events - 1


#@ requires events >= 0
#@ ensures \result >= 0
#@ ensures \result <= 1
def test_empty_after_zero(events: int) -> int:
    """Empty returns 1 if events == 0."""
    if events == 0:
        return 1
    return 0
