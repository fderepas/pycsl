r"""Test 1508 - ROUTE #151 (gen #29): the same class; `P(3).y == 3` PROVED; CPython 5 (the field keeps its default).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field
_ = 0  # anchor


@dataclass
class P:
    y: int = field(init=False, default=5)
    x: int = 0


#@ ensures \result == 3
#@ assigns \nothing
def probe() -> int:
    p = P(3)
    return p.y

