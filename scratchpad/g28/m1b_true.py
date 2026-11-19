r"""M1b — the MI-order carrier read through an INHERITED METHOD (a base field cannot be
read directly: `o.afld` emits the unmangled name and type-errors, so that probe is
vacuous). CPython: `Cee(1, 2, 3)` binds bfld=1, afld=2 (REVERSED MRO), so `get()` is 2."""
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
