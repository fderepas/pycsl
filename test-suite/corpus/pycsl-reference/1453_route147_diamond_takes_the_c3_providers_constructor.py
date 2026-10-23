r"""Test 1453 - ROUTE #147, the FAITHFUL direction for the DIAMOND: `Dee(Bee, Cee)(7).get()` is 107, the C3 MRO's provider, and PROVES.
"""
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


#@ ensures \result == 107
#@ assigns \nothing
def probe() -> int:
    o = Dee(7)
    return o.get()
