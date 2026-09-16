r"""Test 1461 - ROUTE #147, a SHAPE gen #28 missed (gen #29, LIVE at `da51d62b` too): `@dataclass(init=False)` generates NO constructor, so `Cee(7)` runs the plain base's `__init__` storing `afld + 100`. #147 excluded every decorated class and #144 synthesized one, so `Cee(7).get() == 0` PROVED; CPython 107.
"""
# pycsl-expected: FAIL
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


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    o = Cee(7)
    return o.get()

