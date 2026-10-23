"""Test 1058 — ROUTE #44 negative witness (a): a `None`-bound local WAS the integer 0.

FALSE OF THE PROGRAM: `None == 0` is False in Python, so `f()` returns 0.

`x = None` bound the local to the literal `0`, so the guard read `!x = 0` — decidably
TRUE. At the parent commit d0493cea `\\result == 7` PROVED. This is the campaign's
general shape a FIFTH time: a Python singleton modelled as an integer literal is
indistinguishable from that integer inside the model (route #40 was `...`, route #43 the
complex literal, route #42 the bool singleton).
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = None
    if x == 0:
        return 7
    return 0
