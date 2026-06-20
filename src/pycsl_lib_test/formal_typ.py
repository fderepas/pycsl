# Formal tests for pycsl_lib/typ — typing module
from pycsl_lib.typ import cast, get_type_hints


#@ requires val >= 0
#@ ensures \result >= 0
def test_cast_preserves(val: int) -> int:
    """cast returns the value."""
    return cast(0, val)


#@ requires obj >= 0
#@ ensures \result >= 0
def test_hints_nonneg(obj: int) -> int:
    """get_type_hints returns non-negative."""
    return get_type_hints(obj)
