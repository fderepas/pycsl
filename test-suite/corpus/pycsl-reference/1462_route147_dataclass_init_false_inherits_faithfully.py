r"""Test 1462 - ROUTE #147 (gen #29) positive twin of 1461: `@dataclass(init=False)` inherits the base's constructor, and `Cee(7).get() == 107` now PROVES (FAILS at `da51d62b`).
"""
from dataclasses import dataclass
_ = 0  # anchor


class Ay:
    afld: int

    def __init__(self, afld: int) -> None:
        self.afld = afld + 100

    #@ requires True
    #@ ensures \result == self.afld
    def get(self) -> int:
        return self.afld


@dataclass(init=False)
class Cee(Ay):
    cfld: int = 3


#@ ensures \result == 107
#@ assigns \nothing
def probe() -> int:
    o = Cee(7)
    return o.get()

