# Formal tests for pycsl_lib/typ — cast shim (runtime plane, CR1/CR2)
# Spec's promise (cast-twoplane-spec.md §2): cast returns v unchanged, no
# conversion, no type check (the degenerate no-blend case).
from pycsl_lib.typ import cast


#@ requires val >= 0
#@ ensures \result == val
def test_cast_identity(val: int) -> int:
    """cast(typ, val) returns val unchanged (CR1)."""
    return cast(0, val)


#@ requires val >= 0
#@ ensures \result == val
def test_cast_no_conversion(val: int) -> int:
    """cast performs no type conversion — the original value (CR2)."""
    return cast(1, val)
