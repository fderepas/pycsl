# Formal tests for pycsl_lib/typ — Union shim (runtime plane, R1-R8)
# Per pycsl-stdlib-coverage Step 5: consequence driver over universal inputs.
# The spec's promise (union-twoplane-spec.md §2 R3/R8): the shim is identity,
# NO enforcement of arm membership. Re-proved for ALL val.
from pycsl_lib.typ import Union


#@ requires val >= 0
#@ ensures \result == val
def test_union_identity(val: int) -> int:
    """Union(x0, x1, val) returns val unchanged (R3 no enforcement)."""
    return Union(0, 1, val)


#@ requires val >= 0
#@ ensures \result == val
def test_union_no_validation(val: int) -> int:
    """Union does not validate arm membership (R8) — any val passes."""
    return Union(0, 1, val)
