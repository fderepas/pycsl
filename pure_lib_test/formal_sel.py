# Formal tests for pure_lib/sel — selectors module
from pure_lib.sel import EVENT_READ, EVENT_WRITE


#@ ensures \result == 1
def test_event_read() -> int:
    """EVENT_READ is 1."""
    return EVENT_READ


#@ ensures \result == 2
def test_event_write() -> int:
    """EVENT_WRITE is 2."""
    return EVENT_WRITE
