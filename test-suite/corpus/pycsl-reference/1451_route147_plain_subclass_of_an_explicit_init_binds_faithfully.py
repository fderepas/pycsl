r"""Test 1451 - ROUTE #147, the FAITHFUL direction with no `@dataclass` anywhere: `Cee(7).get()` is 7 and PROVES.
"""
_ = 0  # anchor


class Ay:
    def __init__(self, afld: int) -> None:
        self.afld = afld

    #@ requires True
    #@ ensures \result == self.afld
    def get(self) -> int:
        return self.afld


class Cee(Ay):
    pass


#@ ensures \result == 7
#@ assigns \nothing
def probe() -> int:
    o = Cee(7)
    return o.get()
