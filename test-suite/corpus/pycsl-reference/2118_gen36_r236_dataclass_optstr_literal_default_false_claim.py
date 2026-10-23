r"""Test 2118 — route #236 (expected FAIL): an omitted `name: Optional[str] = "w"` (int
carrier, so finding-0700's string capture does not apply) took the definite `0`, so `p.name == "w"`
was decided False and `\result == 0` PROVED; CPython returns 1. The field is now unconstrained.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Optional


@dataclass
class P:
    x: int
    name: Optional[str] = "w"


#@ ensures \result == 0
#@ assigns \nothing
def g(c: int) -> int:
    p = P(c)
    if p.name == "w":
        return 1
    return 0
