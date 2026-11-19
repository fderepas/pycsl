r"""Test 2114 — route #236 (expected FAIL): an omitted `b: Optional[bool] = None` read as
`False` (`0`): `p.b == False` was decided True and `\result == 1` PROVED; CPython `None == False`
is False and `g` returns 2.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Optional


@dataclass
class P:
    x: int
    b: Optional[bool] = None


#@ ensures \result == 1
#@ assigns \nothing
def g(c: int) -> int:
    p = P(c)
    if p.b == False:
        return 1
    return 2
