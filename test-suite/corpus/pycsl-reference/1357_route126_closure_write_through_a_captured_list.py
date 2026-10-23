r"""Test 1357 — ROUTE #126: a nested `walk()` writes `found[0] = 1` through the enclosing function's list; the lifted body wrote an opaque GLOBAL `found`, the enclosing function kept its own, and `\result == 0` PROVED while CPython returns 1. Now refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import List


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    found: List[int] = [0]

    def walk() -> None:
        found[0] = 1

    walk()
    return found[0]
