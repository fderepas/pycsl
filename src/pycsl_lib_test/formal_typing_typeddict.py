# Formal tests for pycsl_lib/typ — TypedDict shim (runtime plane, R3/R7)
# Spec's promise (typeddict-twoplane-spec.md §2): TypedDict alias is identity,
# no enforcement of keys/types (R3/R7). A TypedDict is a plain dict at runtime.
from pycsl_lib.typ import TypedDict


#@ requires val >= 0
#@ ensures \result == val
def test_typeddict_identity(val: int) -> int:
    """TypedDict(typename, fields, val) returns val unchanged (R3)."""
    return TypedDict(0, 0, val)


#@ requires val >= 0
#@ ensures \result == val
def test_typeddict_no_key_check(val: int) -> int:
    """TypedDict does not validate keys/types (R7 no validation)."""
    return TypedDict(0, 0, val)
