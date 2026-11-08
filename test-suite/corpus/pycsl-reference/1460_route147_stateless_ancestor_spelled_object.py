r"""Test 1460 - ROUTE #147, CARRIER-RERUN on gen #29's second fence (walk through `object` only): a stateless user class named `object` ahead of `Ay` PROVED `Cee(7).get() == 7`; CPython gives 5. No unmodelled ancestor is walked through; the real `object` is last in every C3 MRO.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class object:
    def __init__(self, afld: int) -> None:
        pass


class Ay:
    afld: int = 5

    def __init__(self, afld: int) -> None:
        self.afld = afld

    #@ requires True
    #@ ensures \result == self.afld
    def get(self) -> int:
        return self.afld


class Cee(object, Ay):
    pass


#@ ensures \result == 7
#@ assigns \nothing
def probe() -> int:
    o = Cee(7)
    return o.get()

