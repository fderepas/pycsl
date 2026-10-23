r"""Test 1314 — ROUTE #115 second carrier (order 2): `fs[0](x)` — the shape route #24's opaque_dynamic_call comment claims to cover — never reached that arm; Module 5 made it UnknownPyExpr and Module 6 lowered it to 0, so `\result == 0` PROVED (CPython 1 for fs=[lambda y: y+1]).
"""
# pycsl-expected: FAIL
from typing import Callable, List

#@ requires len(fs) > 0
#@ ensures \result == 0
#@ assigns \nothing
def f(fs: List[Callable[[int], int]], x: int) -> int:
    return fs[0](x)
