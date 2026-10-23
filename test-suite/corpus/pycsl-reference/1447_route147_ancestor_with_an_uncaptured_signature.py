r"""Test 1447 - ROUTE #147, CARRIER-RERUN on the repair's own first draft: the MRO walk must stop at the first ancestor that DECLARES a constructor, not the first whose parameters were CAPTURED. `class Bee(Ay): def __init__(self, *args)` has a signature this front end does not capture, so draft 1 stepped PAST it to `Ay`'s and PROVED `Cee(7).get() == 7` where CPython gives 0. A `has_own_init` marker now stops the walk there, copying nothing.
"""
# pycsl-expected: FAIL
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
