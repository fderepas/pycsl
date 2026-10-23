r"""Test 1434 - ROUTE #144 shape B, the FAITHFUL direction: with the `ClassVar` dropped from the binding list, `P(1, 2)` binds x=1, y=2 and `\result == 1` PROVES, matching CPython.
"""
from dataclasses import dataclass
from typing import ClassVar

_ = 0  # anchor


@dataclass
class P:
    k: ClassVar[int] = 10
    x: int
    y: int


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    p = P(1, 2)
    return p.x
