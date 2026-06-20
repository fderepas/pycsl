# Formal tests for pycsl_lib/pkl — pickle module
from pycsl_lib.pkl import dumps, loads


#@ requires size >= 0
#@ ensures \result >= 0
def test_dumps_nonneg(size: int) -> int:
    """dumps returns non-negative."""
    return dumps(size)


#@ requires data >= 0
#@ ensures \result >= 0
def test_loads_nonneg(data: int) -> int:
    """loads returns non-negative."""
    return loads(data)
