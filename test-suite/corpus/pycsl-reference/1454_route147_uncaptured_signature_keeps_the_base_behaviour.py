r"""Test 1454 - ROUTE #147 control: with the walk stopping at the `*args` ancestor and copying nothing, the subclass keeps the pre-existing all-defaults behaviour, which here HAPPENS to be the truth - `Cee(7).get()` is 0, matching CPython. PASSES on both sides of the repair; it is the negative control for 1447.
"""
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


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    o = Cee(7)
    return o.get()
