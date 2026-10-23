r"""Test 1435 - ROUTE #144, the FAITHFUL direction for MULTIPLE inheritance: `Cee(Ay, Bee)(1, 2, 3)` binds bfld=1, afld=2 as Python does, so the inherited `get()` returns 2 and `\result == 2` PROVES.
"""
from dataclasses import dataclass

_ = 0  # anchor


@dataclass
class Ay:
    afld: int

    #@ requires True
    #@ ensures \result == self.afld
    def get(self) -> int:
        return self.afld


@dataclass
class Bee:
    bfld: int


@dataclass
class Cee(Ay, Bee):
    cfld: int


#@ ensures \result == 2
#@ assigns \nothing
def probe() -> int:
    o = Cee(1, 2, 3)
    return o.get()
