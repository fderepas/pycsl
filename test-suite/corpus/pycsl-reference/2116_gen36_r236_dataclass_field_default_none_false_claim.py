r"""Test 2116 — route #236 (expected FAIL): the `field(default=None)` spelling of 2110:
`p.k == 0` PROVED at base; CPython `None`.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class P:
    x: int
    k: Optional[int] = field(default=None)


#@ ensures \result == 1
#@ assigns \nothing
def g(c: int) -> int:
    p = P(c)
    if p.k == 0:
        return 1
    return 2
