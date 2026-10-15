r"""Test 2212 — route #239 (expected PASS): CONTROL for 2202. Two calls `g(y)` with the SAME
actual: `g`'s postcondition is now about `typeof_op y` in both, so the results agree and
`\result == 1` PROVES (CPython: 1 for any `y`).
"""
# pycsl-expected: PASS
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
