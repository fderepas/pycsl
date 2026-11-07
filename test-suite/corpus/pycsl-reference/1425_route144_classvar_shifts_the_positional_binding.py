r"""Test 1425 - ROUTE #144 shape B: a `ClassVar` member is an `ast.AnnAssign` and entered `init_params`, but Python does NOT make it an `__init__` parameter, so the whole positional binding was OFF BY ONE and each field took its NEIGHBOUR's argument - a DEFINITE WRONG VALUE, not a lost default. `\result == 2` PROVED while CPython returns 1. `ClassVar` members are now dropped from the synthesized binding list.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import ClassVar

_ = 0  # anchor


@dataclass
class P:
    k: ClassVar[int] = 10
    x: int
    y: int


#@ ensures \result == 2
#@ assigns \nothing
def probe() -> int:
    p = P(1, 2)
    return p.x
