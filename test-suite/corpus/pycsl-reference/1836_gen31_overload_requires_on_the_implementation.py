r"""Test 1836 — ROUTE #222 CONTROL (expected FAIL): the same precondition, correctly placed.

1834 with `#@ requires x > 100` moved from the `@overload` stub to the IMPLEMENTATION. The
call `f(0)` violates it and the file FAILS on the call-site precondition — which is what
makes 1834 a route and not a missing feature: the precondition machinery was never broken,
it was bypassed by where the clause was written.
"""
# pycsl-expected: FAIL
from typing import overload
_ = 0  # anchor


@overload
def f(x: int) -> int: ...


#@ requires x > 100
#@ ensures \result == x
def f(x: int) -> int:
    return x


#@ ensures \result == 0
def use() -> int:
    return f(0)
