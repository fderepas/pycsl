# Formal tests for pure_lib/reprlib
from pure_lib.reprlib import repr_bounded, repr_with_limit


#@ requires obj >= 0
#@ ensures \result >= 0
#@ ensures \result <= obj
def test_repr_bounded(obj: int) -> int:
    """repr output <= input (truncation)."""
    return repr_bounded(obj)


#@ requires maxlevel >= 0
#@ requires obj >= 0
#@ ensures \result >= 0
#@ ensures \result <= obj
def test_repr_with_limit(maxlevel: int, obj: int) -> int:
    """repr with limit also bounded by object size."""
    return repr_with_limit(maxlevel, obj)
