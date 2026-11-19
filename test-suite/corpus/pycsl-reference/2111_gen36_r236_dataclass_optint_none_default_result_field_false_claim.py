r"""Test 2111 — route #236 (expected FAIL): the route's `\result.k == 0` spelling over
an omitted `k: Optional[int] = None` — PROVED at base (`{ x = c; k = 0 }`), CPython `None`.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Optional


@dataclass
class P:
    x: int
    k: Optional[int] = None


#@ ensures \result.k == 0
#@ assigns \nothing
def f(c: int) -> P:
    return P(c)
