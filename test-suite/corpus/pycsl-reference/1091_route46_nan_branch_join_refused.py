"""Test 1091 — ROUTE #46 negative witness (NaN half): A COMPARISON OVER A POSSIBLY-NaN NAME.

FALSE OF THE PROGRAM: `nan == nan` is False in Python, so `f(1)` returns 0.

The same join, the other record. Route #45 lowers a NaN-bound local's comparisons EXACTLY —
every ordering and `==` False, `!=` True — and its record is linear too, so the `else`
branch's `x = 1` cleared it and the guard fell through to ordinary int reflexivity.
`\\result == 7` PROVED at 90fed0c9, i.e. WITH route #45's fix in place.

WHY THIS HALF IS A REFUSAL AND THE `None` HALF IS NOT, and it is route #45's lesson stated
once more: making the value OPAQUE does not close it. An opaque constant is still EQUAL TO
ITSELF, so `x == x` would stay decidably true. NaN is the one Python value whose `==` is not
reflexive and no int model can express that, so a comparison over a name that MAY be NaN is
rejected outright (`PYCSL-WHYML-AMBIGUOUS-NAN-COMPARISON`). The taint follows arithmetic:
IEEE 754 makes every operation with a NaN operand NaN, so `y = x + 1` is possibly-NaN too.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ requires c > 0
#@ ensures \result == 7
#@ assigns \nothing
def f(c: int) -> int:
    if c > 0:
        x = float("nan")
    else:
        x = 1
    if x == x:
        return 7
    return 0


if __name__ == "__main__":
    assert f(1) == 0
