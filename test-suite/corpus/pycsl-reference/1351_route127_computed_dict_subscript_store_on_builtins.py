r"""Test 1351 — ROUTE #127: `getattr(__builtins__, "__dict__")["len"] = seven` writes the builtins namespace through a COMPUTED receiver; `len([1, 2])` PROVED `\result == 2` while CPython (run as a script) returns 7. Now refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import List


def seven(xs: List[int]) -> int:
    return 7


getattr(__builtins__, "__dict__")["len"] = seven


#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    xs: List[int] = [1, 2]
    return len(xs)
