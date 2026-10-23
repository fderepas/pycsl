r"""Test 1883 — gen #31 CONTROL for 1882 (expected PASS): a resolvable reveal still verifies.

The same file revealing a function that exists. Within the owning unit `#@ reveal` is a
documented no-op (§2.10 — the definition IS the visible `let`), and that stays true: what
the refusal checks is that the NAME RESOLVES, not that the reveal has an effect here. The
cross-module pair that gives it an effect is 1867/1868.
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ requires a > 0
#@ ensures \result == a
#@ assigns \nothing
def inner(a: int) -> int:
    return a


#@ reveal inner
#@ requires x > 0
#@ ensures \result == x
#@ assigns \nothing
def caller(x: int) -> int:
    return inner(x)
