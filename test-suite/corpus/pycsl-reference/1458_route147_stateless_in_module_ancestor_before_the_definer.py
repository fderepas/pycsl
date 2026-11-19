r"""Test 1458 - ROUTE #147, CARRIER-RERUN (gen #29): an in-module STATELESS base `Mid` (no fields, so no record) defines a constructor and precedes `Ay` in the MRO. Draft 4 walked past it and `Cee(7).get() == 7` PROVED; CPython gives 5.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class Mid:
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


class Cee(Mid, Ay):
    pass


#@ ensures \result == 7
#@ assigns \nothing
def probe() -> int:
    o = Cee(7)
    return o.get()

