r"""Test 2113 — route #236 (expected FAIL): an omitted `items: Optional[List[int]] = None`
(int carrier) lowered to the definite `0` and `\result.items == 0` PROVED; CPython `None`.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class P:
    x: int
    items: Optional[List[int]] = None


#@ ensures \result.items == 0
#@ assigns \nothing
def f(c: int) -> P:
    return P(c)
