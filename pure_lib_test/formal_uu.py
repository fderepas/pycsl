# Formal tests for pure_lib/uu — uuid module
from pure_lib.uu import uuid1, uuid4, uuid3, uuid5


#@ ensures \result >= 0
def test_uuid1_nonneg() -> int:
    """uuid1 returns non-negative."""
    return uuid1()


#@ ensures \result >= 0
def test_uuid4_nonneg() -> int:
    """uuid4 returns non-negative."""
    return uuid4()


#@ requires name >= 0
#@ ensures \result >= 0
def test_uuid3_nonneg(name: int) -> int:
    """uuid3 returns non-negative."""
    return uuid3(name)
