r"""Q4 — carrier-rerun on route #147: the inherited constructor has KEYWORD-ONLY
parameters (the shape the mirror's own `PyCSLError` hierarchy actually uses)."""
_ = 0  # anchor


class Ay:
    afld: int
    bfld: int

    def __init__(self, afld: int, *, bfld: int = 3) -> None:
        self.afld = afld
        self.bfld = bfld

    #@ requires True
    #@ ensures \result == self.bfld
    def get(self) -> int:
        return self.bfld


class Cee(Ay):
    pass


#@ ensures \result == 9
#@ assigns \nothing
def probe() -> int:
    o = Cee(1, bfld=9)
    return o.get()
