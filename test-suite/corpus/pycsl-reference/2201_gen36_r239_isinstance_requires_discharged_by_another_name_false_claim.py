r"""Test 2201 — route #239 (expected FAIL): in a CONTRACT the name-keyed tag did not mention the
argument at all. `g`'s `requires isinstance(x, int)` was `subtag (typeof_op 120) tag_int`, the
SAME closed formula as `m`'s own precondition about ITS `x`, so `m` discharged `g`'s
precondition for the call `g(y)` and `\result == 1` PROVED at f926a808 — CPython `m(1, "s")`
calls `g("s")` outside its precondition and returns 0. Now `g`'s precondition is about the
actual (`typeof_op y` at the call) and is not provable from a fact about `x`.
"""
# pycsl-expected: FAIL
from typing import Any


#@ requires isinstance(x, int)
#@ ensures \result == 1
#@ assigns \nothing
def g(x: Any) -> int:
    if isinstance(x, int):
        return 1
    return 0


#@ requires isinstance(x, int)
#@ ensures \result == 1
#@ assigns \nothing
def m(x: Any, y: Any) -> int:
    return g(y)
