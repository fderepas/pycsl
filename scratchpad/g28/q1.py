r"""Q1 — carrier-rerun on gen #28's own route-#147 repair: the MRO walk must stop at the
first ancestor that DECLARES a constructor, not at the first whose parameters were
CAPTURED. `Bee` declares `__init__(self, *args)`, whose params this front end does not
capture, so a walk keyed on "non-empty init_params" skips past it to `Ay`'s — a
constructor Python never calls here."""
_ = 0  # anchor


class Ay:
    def __init__(self, afld: int) -> None:
        self.afld = afld

    #@ requires True
    #@ ensures \result == self.afld
    def get(self) -> int:
        return self.afld


class Bee(Ay):
    def __init__(self, *args) -> None:
        self.afld = 0


class Cee(Bee):
    pass


#@ ensures \result == 7
#@ assigns \nothing
def probe() -> int:
    o = Cee(7)
    return o.get()
