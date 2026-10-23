r"""M1 — carrier-rerun on gen #28's own route-#144 repair: MULTIPLE INHERITANCE.
Python's @dataclass builds its field list from the REVERSED MRO, so `Cee(Ay, Bee)` takes
Bee's fields FIRST, then Ay's, then its own: `Cee(1, 2, 3)` binds bfld=1, afld=2, cfld=3.
A merge that walks the DECLARED bases in declaration order binds afld=1 instead."""
from dataclasses import dataclass

_ = 0  # anchor


@dataclass
class Ay:
    afld: int


@dataclass
class Bee:
    bfld: int


@dataclass
class Cee(Ay, Bee):
    cfld: int


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    o = Cee(1, 2, 3)
    return o.afld
