r"""Test 1481 - ROUTE #149 x #147 (gen #29): `Bee(Ay)` inherits `Ay.__init__(self, r: int = 5)`; `Bee().get() == 0` PROVED at HEAD, CPython 5. The parameter defaults travel with the copied constructor.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class Ay:
    def __init__(self, r: int = 5) -> None:
        self.r = r

    #@ requires True
    #@ ensures \result == self.r
    def get(self) -> int:
        return self.r


class Bee(Ay):
    pass


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    b = Bee()
    return b.get()

