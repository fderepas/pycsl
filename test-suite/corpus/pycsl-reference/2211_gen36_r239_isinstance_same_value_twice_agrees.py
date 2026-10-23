r"""Test 2211 — route #239 (expected PASS): CONTROL. Two tests of ONE unchanged value agree —
`typeof_op x` twice is one term — so `\result == 1` PROVES (CPython: 1 for any `x`). The
value-keyed tag keeps the equality the name-keyed one was right about.
"""
# pycsl-expected: PASS
from typing import Any


#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any) -> int:
    a = 0
    if isinstance(x, int):
        a = 1
    b = 0
    if isinstance(x, int):
        b = 1
    if a == b:
        return 1
    return 0
