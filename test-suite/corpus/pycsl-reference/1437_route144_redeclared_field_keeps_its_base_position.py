r"""Test 1437 - ROUTE #144: a field REDECLARED in the subclass keeps its BASE POSITION (PEP 557), so `Cee(1, 2)` binds the inherited `afld` from argument 0 even though `afld` is redeclared AFTER `cfld` in the subclass body. The inherited `get()` returns 1 and PROVES.
"""
from dataclasses import dataclass

_ = 0  # anchor


@dataclass
class Ay:
    afld: int = 0


@dataclass
class Cee(Ay):
    cfld: int = 0
    afld: int = 0

    #@ requires True
    #@ ensures \result == self.afld
    def get(self) -> int:
        return self.afld


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    o = Cee(1, 2)
    return o.get()
