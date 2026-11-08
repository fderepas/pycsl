r"""Test 2212 — route #239 (expected PASS until route #246; expected FAIL now): CONTROL for 2202.
Two calls `g(y)` with the SAME actual: `g`'s postcondition was about `typeof_op y` in both, so the
results agreed and `\result == 1` PROVED (CPython: 1 for any `y`). Route #246: that postcondition is
a function of the STORED int, so the same proof with two `==` actuals of different types (`1`, `1.0`)
also PROVED a false claim (corpus 2325). A contract-side `isinstance(<Any>, int)` is now REFUSED at
the WhyML type-check (fail-closed); this true claim is the price of that refusal.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 0 or \result == 1
#@ ensures \result == 1 <==> isinstance(x, int)
#@ assigns \nothing
def g(x: Any) -> int:
    if isinstance(x, int):
        return 1
    return 0


#@ ensures \result == 1
#@ assigns \nothing
def m(y: Any) -> int:
    a = g(y)
    b = g(y)
    if a == b:
        return 1
    return 0
