# Formal tests for pycsl_lib/typ — overload shim (runtime plane, R3/R6)
# Spec's promise (overload-twoplane-spec.md §2): @overload stubs discarded at
# runtime; the shim is identity, no validation (R3/R6).
from pycsl_lib.typ import overload


#@ requires val >= 0
#@ ensures \result == val
def test_overload_identity(val: int) -> int:
    """overload(func, val) returns val unchanged (R3 no enforcement)."""
    return overload(0, val)


#@ requires val >= 0
#@ ensures \result == val
def test_overload_no_validation(val: int) -> int:
    """overload does not validate the stub family (R6)."""
    return overload(0, val)
