r"""Test 2112 — route #236 (expected FAIL): an omitted `name: Optional[str] = None` (int
carrier) lowered to the definite `0` and `\result.name == 0` PROVED; CPython `None`.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Optional


@dataclass
class P:
    x: int
    name: Optional[str] = None


#@ ensures \result.name == 0
#@ assigns \nothing
def f(c: int) -> P:
    return P(c)
