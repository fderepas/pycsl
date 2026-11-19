r"""Test 1445 - ROUTE #147, the same defect with no `@dataclass` anywhere: a plain base with an explicit `__init__` and a plain subclass with none. `Cee(7).get() == 0` PROVED while CPython returns 7.
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


class Cee(Ay):
    pass


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    o = Cee(7)
    return o.get()
