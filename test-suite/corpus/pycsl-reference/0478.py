"""Test 0478 — strings: __le__ (`s <= t`, lexicographic).
Target: lexicographic comparison. PROVES as of the G2 strings feature: `<=` over two string
operands lowers to `str_le_op` (a `val:bool` bridge tied by `ensures` to the Why3 lexicographic
predicate `String.le`); the body returns Python's int truth value (`if … then 1 else 0`)."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(s) >= 0
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def le(s: str, t: str) -> bool:
    return s <= t
