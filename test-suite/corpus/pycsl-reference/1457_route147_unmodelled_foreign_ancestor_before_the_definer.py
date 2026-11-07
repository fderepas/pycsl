r"""Test 1457 - ROUTE #147, CARRIER-RERUN on the repair's own draft 4 (gen #29): `class Cee(Exception, Ay): pass`. The C3 MRO is Cee, Exception, Ay and Python calls BaseException's constructor, which binds no field; the walk `continue`d past the UNMODELLED name and copied `Ay`'s, so `Cee(7).get() == 7` PROVED while CPython gives the class-level default 5. Any unmodelled ancestor now STOPS the walk.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class Ay:
    afld: int = 5

    def __init__(self, afld: int) -> None:
        self.afld = afld

    #@ requires True
    #@ ensures \result == self.afld
    def get(self) -> int:
        return self.afld


class Cee(Exception, Ay):
    pass


#@ ensures \result == 7
#@ assigns \nothing
def probe() -> int:
    o = Cee(7)
    return o.get()

