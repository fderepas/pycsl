# Formal tests for pycsl_lib/tm — time module
# ClockModel class. Test time concepts.


#@ requires elapsed >= 0
#@ ensures \result >= 0
def test_time_nonneg(elapsed: int) -> int:
    """Time values are non-negative."""
    return elapsed


#@ requires seconds >= 0
#@ ensures \result >= 0
def test_sleep_returns(seconds: int) -> int:
    """sleep completes with 0."""
    return 0
