r"""Test 2252 — route #241 (expected PASS): CONTROL. A generator actual whose value the callee
never inspects stays fine: `g` returns 7 whatever it is given, so `\result == 7` PROVES with the
actual now `(any int)` (CPython: 7).
"""
# pycsl-expected: PASS
from typing import Any


#@ ensures \result == 7
#@ assigns \nothing
def g(x: Any) -> int:
    return 7


#@ ensures \result == 7
#@ assigns \nothing
def m() -> int:
    return g(v for v in [1])
