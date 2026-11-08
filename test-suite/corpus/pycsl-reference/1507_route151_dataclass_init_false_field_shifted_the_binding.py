r"""Test 1507 - ROUTE #151 (gen #29): `@dataclass` with `y: int = field(init=False, default=5)` before `x: int = 0`; the synthesized `init_params` included `y`, so `P(3)` gave `{ y = 3; x = 0 }` and `P(3).x == 0` PROVED; CPython 3. A `field(init=False)` field is not a parameter.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field
_ = 0  # anchor


@dataclass
class P:
    y: int = field(init=False, default=5)
    x: int = 0


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    p = P(3)
    return p.x

