r"""Test 1450 - ROUTE #147, the FAITHFUL direction: the undecorated subclass now carries the base's constructor and `Cee(7).get()` is 7, matching CPython. FAILED before the repair.
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
    pass


#@ ensures \result == 7
#@ assigns \nothing
def probe() -> int:
    o = Cee(7)
    return o.get()
