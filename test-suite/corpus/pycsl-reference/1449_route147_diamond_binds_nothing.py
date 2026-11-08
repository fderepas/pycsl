r"""Test 1449 - ROUTE #147, the DIAMOND as it stood before any repair: `Dee(7)` bound nothing at all and `get() == 0` PROVED while CPython returns 107. 1448 is the twin that an intermediate draft made provable.
"""
# pycsl-expected: FAIL
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


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    o = Dee(7)
    return o.get()
