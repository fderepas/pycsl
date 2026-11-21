r"""Test 2126 — route #236 (expected FAIL): 2124 with `name: Optional[str] = None`:
`p.name == 0` PROVED at base; CPython `None`.
"""
# pycsl-expected: FAIL
from typing import Optional


class P:
    def __init__(self, x: int, name: Optional[str] = None) -> None:
        self.x = x
        self.name = name


#@ ensures \result == 1
#@ assigns \nothing
def g(c: int) -> int:
    p = P(c)
    if p.name == 0:
        return 1
    return 2
