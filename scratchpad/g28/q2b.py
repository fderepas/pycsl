r"""Q2 — carrier-rerun on route #147: a DIAMOND. `Dee(Bee, Cee)` where `Bee` declares no
constructor and `Cee` does; the C3 MRO is Dee, Bee, Cee, Ay, so Python calls Cee's."""
_ = 0  # anchor


class Ay:
    afld: int

    def __init__(self, afld: int) -> None:
        self.afld = afld

    #@ requires True
    #@ ensures \result == self.afld
    def get(self) -> int:
        return self.afld


class Bee(Ay):
    pass


class Cee(Ay):
    def __init__(self, afld: int) -> None:
        self.afld = afld + 100


class Dee(Bee, Cee):
    pass


#@ ensures \result == 7
#@ assigns \nothing
def probe() -> int:
    o = Dee(7)
    return o.get()
