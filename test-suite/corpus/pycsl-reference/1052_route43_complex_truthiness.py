"""Test 1052 — ROUTE #43 negative witness (c): the truthiness of a complex literal.

FALSE OF THE PROGRAM: `bool(3j)` is True, so Python returns 7.

`3j` lowered to the integer `0`, so the guard was decidably FALSE and the branch Python
takes was proved NOT taken. At the parent commit f2873419 `\result == 0` PROVED.

Together with 1050 and 1051 this is #44's rule for the sixth time in the window: AN
ERASURE TO A LITERAL IS ONE `if` AWAY FROM A FALSE PROOF.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    x = 3j
    if x:
        return 7
    return 0
