r"""M5 — a THREE-LEVEL dataclass chain: the grandparent's field must reach the
grandchild's signature. CPython: `Cee(1, 2, 3).cfld` is 3."""
from dataclasses import dataclass

_ = 0  # anchor


@dataclass
class Ay:
    afld: int


@dataclass
class Bee(Ay):
    bfld: int


@dataclass
class Cee(Bee):
    cfld: int


#@ ensures \result == 3
#@ assigns \nothing
def probe() -> int:
    o = Cee(1, 2, 3)
    return o.cfld
