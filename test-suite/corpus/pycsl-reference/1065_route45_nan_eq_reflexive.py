"""Test 1065 — ROUTE #45 negative witness (a): `nan == nan` PROVED.

FALSE OF THE PROGRAM: `float("nan") == float("nan")` is False in Python — NaN is the one
Python value for which `==` is not reflexive — so `f()` returns 0.

`float(<str>)` has no model and lowers to an abstract `val py_float_1 (x0: int) : int`, an
opaque INT, so the guard read `!x = !x`: REFLEXIVITY OF `=`, which every value model has.
At the parent commit 3bbfb59f `\\result == 7` PROVED.

THIS IS WHY THE FIX IS NOT THE CAMPAIGN'S USUAL ONE. Routes #40, #41 and #44 each closed a
wrong-value erasure by making the VALUE OPAQUE — and here the value was ALREADY opaque and
still satisfied `c = c`. Opacity does not repair a broken equivalence relation. What repairs
it is that NaN's comparison semantics are TOTALLY DETERMINED, so the lowering can be exact.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = float("nan")
    if x == x:
        return 7
    return 0
