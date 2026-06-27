# Formal tests for pycsl_lib/typ — NamedTuple shim (runtime plane, R3/R8)
# Spec's promise (namedtuple-twoplane-spec.md §2): NamedTuple alias is identity,
# no enforcement of arity/types (R3/R8). A NamedTuple is a plain tuple at runtime.
from pycsl_lib.typ import NamedTuple


#@ requires val >= 0
#@ ensures \result == val
def test_namedtuple_identity(val: int) -> int:
    """NamedTuple(typename, fields, val) returns val unchanged (R3)."""
    return NamedTuple(0, 0, val)


#@ requires val >= 0
#@ ensures \result == val
def test_namedtuple_no_arity_check(val: int) -> int:
    """NamedTuple does not validate arity/types (R8 no validation)."""
    return NamedTuple(0, 0, val)
