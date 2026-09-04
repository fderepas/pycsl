"""Test 1021 — ROUTE #34: the mutation happens in a CALLEE.

FALSE OF THE PROGRAM: `g` writes `a[0] = 9` through the list it was passed, so
Python returns 9. Proved `\result == 5` at c4233fed.

`g` declares `assigns z[0..0]` and is honest about it; the caller's fold simply
never asked. A name handed to a call that is not one of a short list of
non-mutating builtins is now unfoldable.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires \length(z) >= 1
#@ assigns z[0..0]
def g(z: list) -> int:
    z[0] = 9
    return 0

#@ ensures \result == 5
def f() -> int:
    a = [5]
    g(a)
    return a[0]
