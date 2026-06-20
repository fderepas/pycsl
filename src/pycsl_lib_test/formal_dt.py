# Formal tests for pycsl_lib/dt — datetime module
from pycsl_lib.dt import now, timedelta_seconds, fromtimestamp


#@ ensures \result >= 0
def test_now_nonneg() -> int:
    """now returns non-negative."""
    return now()


#@ requires days >= 0
#@ ensures \result >= 0
def test_timedelta_nonneg(days: int) -> int:
    """timedelta_seconds returns non-negative."""
    return timedelta_seconds(days)


#@ requires ts >= 0
#@ ensures \result >= 0
def test_fromtimestamp_nonneg(ts: int) -> int:
    """fromtimestamp returns non-negative."""
    return fromtimestamp(ts)
