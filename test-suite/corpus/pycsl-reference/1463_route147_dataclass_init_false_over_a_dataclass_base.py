r"""Test 1463 - ROUTE #147 (gen #29) control: `@dataclass(init=False)` over a `@dataclass` base inherits the base's synthesized `__init__(afld)`, so `Cee(7).get() == 7` - PROVES on both sides of the repair (formerly through #144's synthesize arm, now through the inherit walk).
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


@dataclass(init=False)
class Cee(Ay):
    cfld: int = 3


#@ ensures \result == 7
#@ assigns \nothing
def probe() -> int:
    o = Cee(7)
    return o.get()

