r"""Test 2125 — route #236 (expected FAIL): the keyword-only twin of 2124
(`*, k: Optional[int] = None`): `p.k == 0` PROVED at base; CPython `None`.
"""
# pycsl-expected: FAIL
from typing import Optional


class P:
    def __init__(self, x: int, *, k: Optional[int] = None) -> None:
        self.x = x
        self.k = k


#@ ensures \result == 1
#@ assigns \nothing
def g(c: int) -> int:
    p = P(c)
    if p.k == 0:
        return 1
    return 2
