r"""Test 1452 - ROUTE #147, the FAITHFUL direction for the inert-annotation shape: the subclass's own `cfld: int = 0` does NOT become a constructor parameter (Python never ran the decorator on it) and `Cee(7).get()` is 7.
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


class Cee(Ay):
    cfld: int = 0


#@ ensures \result == 7
#@ assigns \nothing
def probe() -> int:
    o = Cee(7)
    return o.get()
