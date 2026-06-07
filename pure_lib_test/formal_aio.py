# Formal tests for pure_lib/aio — asyncio module
from pure_lib.aio import get_event_loop, sleep, gather


#@ ensures \result >= 0
def test_get_loop_nonneg() -> int:
    """get_event_loop returns non-negative."""
    return get_event_loop()


#@ requires delay >= 0
#@ ensures \result >= 0
def test_sleep_nonneg(delay: int) -> int:
    """sleep returns non-negative."""
    return sleep(delay)


#@ requires count >= 0
#@ ensures \result >= 0
def test_gather_nonneg(count: int) -> int:
    """gather returns non-negative."""
    return gather(count)
