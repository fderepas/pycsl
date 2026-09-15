r"""Test 1340 — ROUTE #121: a user decorator was SILENTLY DROPPED. `@swap` (which returns `abs`) over `inc`; `inc(-3)` PROVED the undecorated contract `\result == -2` while CPython returns 3. A decorator whose effect is not modelled is now refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import Any


def swap(fn: Any) -> Any:
    return abs


#@ ensures \result == y + 1
#@ assigns \nothing
@swap
def inc(y: int) -> int:
    return y + 1


#@ ensures \result == -2
#@ assigns \nothing
def f() -> int:
    return inc(-3)
