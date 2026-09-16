r"""P4 — an UNDECORATED subclass of a @dataclass that declares its OWN annotation: Python
does NOT run @dataclass on it, so `cfld` is a bare annotation and `Cee(7)` calls Ay's
inherited `__init__(afld)`; `Cee(7, 1)` would be a TypeError."""
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
