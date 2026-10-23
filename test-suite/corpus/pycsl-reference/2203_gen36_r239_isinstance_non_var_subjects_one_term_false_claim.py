r"""Test 2203 — route #239 (expected FAIL): a NON-`Var` subject had no name to hash, so EVERY
such test was `typeof_op 0` — `isinstance(xs[0], int)` and `isinstance(xs[1], int)` were one
term and `\result == 1` PROVED at f926a808 while CPython `f([1, "s"])` = 0. Now
`typeof_op (xs[0])` / `typeof_op (xs[1])`.
"""
# pycsl-expected: FAIL
from typing import Any, List


#@ requires len(xs) >= 2
#@ ensures \result == 1
#@ assigns \nothing
def f(xs: List[Any]) -> int:
    a = 0
    if isinstance(xs[0], int):
        a = 1
    b = 0
    if isinstance(xs[1], int):
        b = 1
    if a == b:
        return 1
    return 0
