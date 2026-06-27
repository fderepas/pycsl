# Formal tests for pycsl_lib/typ — Optional shim (runtime plane, OR1-OR8)
# Spec's promise (optional-twoplane-spec.md §2): Optional is Union[X, None];
# the shim is identity, no enforcement.
from pycsl_lib.typ import Union


#@ requires val >= 0
#@ ensures \result == val
def test_optional_identity(val: int) -> int:
    """Optional[X] (= Union[X, None]) shim returns val unchanged (OR3)."""
    return Union(0, 0, val)


#@ requires val >= 0
#@ ensures \result == val
def test_optional_none_arm_no_check(val: int) -> int:
    """The None arm does not validate the value (OR3 no enforcement)."""
    return Union(0, 0, val)
