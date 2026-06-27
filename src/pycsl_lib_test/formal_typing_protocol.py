# Formal tests for pycsl_lib/typ — Protocol / runtime_checkable shim (GT7)
# Spec's promise (protocol-twoplane-spec.md §2): runtime_checkable is identity,
# presence-only, NO signature/behaviour check (the GT7 no-blend keystone).
from pycsl_lib.typ import runtime_checkable


#@ requires val >= 0
#@ ensures \result == val
def test_runtime_checkable_identity(val: int) -> int:
    """runtime_checkable(cls, val) returns val unchanged (R3)."""
    return runtime_checkable(0, val)


#@ requires val >= 0
#@ ensures \result == val
def test_runtime_checkable_no_signature_check(val: int) -> int:
    """runtime_checkable is presence-only, no signature check (GT7 no-blend)."""
    return runtime_checkable(0, val)
