r"""Test 1446 - ROUTE #147, the shape that decides the REPAIR'S FORM: an UNDECORATED subclass of a `@dataclass` that declares its OWN annotation. Python does NOT run the decorator here, so `cfld: int = 0` is an inert annotation and `Cee(7)` still calls the base's `__init__(afld)` - which is why a class that merely INHERITS a constructor must COPY it wholesale rather than SYNTHESIZE one from the merged field list the way route #144 does. `\result == 0` PROVED while CPython returns 7.
"""
# pycsl-expected: FAIL
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


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    o = Cee(7)
    return o.get()
