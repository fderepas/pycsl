r"""Test 1510 - ROUTE #151 (gen #29) positive twin of 1507: `P(3).x == 3` PROVES (FAILS at HEAD).
"""
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
    return p.x

