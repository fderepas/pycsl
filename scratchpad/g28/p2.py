r"""P2 — carrier-rerun on route #144: a PLAIN (undecorated) subclass of a @dataclass
INHERITS the synthesized __init__, read through an inherited method (a direct base-field
read is vacuous). CPython: `Cee(7).get()` is 7."""
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


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    o = Cee(7)
    return o.get()
