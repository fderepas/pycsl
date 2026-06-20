# Formal tests for pycsl_lib/cpmod — copy module
from pycsl_lib.cpmod import copy, deepcopy


#@ requires obj >= 0
#@ ensures \result >= 0
def test_copy_preserves(obj: int) -> int:
    """copy returns non-negative."""
    return copy(obj)


#@ requires obj >= 0
#@ ensures \result >= 0
def test_deepcopy_preserves(obj: int) -> int:
    """deepcopy returns non-negative."""
    return deepcopy(obj)
