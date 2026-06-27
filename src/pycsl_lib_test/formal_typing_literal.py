# Formal tests for pycsl_lib/typ — Literal shim (runtime plane, LR1-LR8)
# Spec's promise (literal-twoplane-spec.md §2): Literal alias is identity,
# no enforcement of the value set (LR3/LR8).
from pycsl_lib.typ import Literal


#@ requires val >= 0
#@ ensures \result == val
def test_literal_identity(val: int) -> int:
    """Literal(x0, x1, val) returns val unchanged (LR3 no enforcement)."""
    return Literal(0, 1, val)


#@ requires val >= 0
#@ ensures \result == val
def test_literal_no_value_set_check(val: int) -> int:
    """Literal does not validate value-set membership (LR8)."""
    return Literal(0, 1, val)
