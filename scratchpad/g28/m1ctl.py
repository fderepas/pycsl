r"""M1ctl — POSITIVE CONTROL for M1b: SINGLE inheritance, where declaration order and
reversed-MRO order agree. `Cee(1, 2)` binds afld=1, cfld=2 in BOTH, so `get()` is 1."""
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
class Cee(Ay):
    cfld: int


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    o = Cee(1, 2)
    return o.get()
