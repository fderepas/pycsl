# Formal tests for pycsl_lib/typ — Final shim (runtime plane, FR3/FR6)
# Spec's promise (final-twoplane-spec.md §2): Final alias is identity, NO
# descriptor, no enforcement of write-once / __init__-only (FR3/FR6).
from pycsl_lib.typ import Final


#@ requires val >= 0
#@ ensures \result == val
def test_final_identity(val: int) -> int:
    """Final(x0, x1, val) returns val unchanged (FR3 no enforcement)."""
    return Final(0, 1, val)


#@ requires val >= 0
#@ ensures \result == val
def test_final_no_descriptor(val: int) -> int:
    """Final does not introduce a write-blocking descriptor (FR6)."""
    return Final(0, 1, val)
