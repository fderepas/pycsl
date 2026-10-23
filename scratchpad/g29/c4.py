r"""G29 C4 — carrier-rerun on route #147 draft 4 / witness 1454's premise: an ancestor with an
UNCAPTURED `*args` constructor that DOES set the field; the walk stops, copies nothing, and the
subclass keeps the all-defaults model. Is that model really fail-closed?"""
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
    def __init__(self, *args: int) -> None:
        self.afld = 9


class Cee(Bee):
    pass


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    o = Cee(7)
    return o.get()


if __name__ == "__main__":
    print("CPython:", probe())
