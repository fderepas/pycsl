r"""Test 1459 - ROUTE #147, CARRIER-RERUN on gen #29's OWN first fence, which let `object`/`Generic`/`ABC` be walked through because CPython defines no constructor on them: a stateless USER class named `ABC` with a constructor PROVED the same false `== 7` (CPython 5). An unmodelled name is only a spelling.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class ABC:
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


class Cee(ABC, Ay):
    pass


#@ ensures \result == 7
#@ assigns \nothing
def probe() -> int:
    o = Cee(7)
    return o.get()

