r"""Test 1491 - ROUTE #149 (gen #29): `def __init__(self, flag: bool = True)` with `Cy()` gave `{ flag = 0 }`, so `if c.flag` was false and `== 0` PROVED; CPython 1.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class Cy:
    def __init__(self, flag: bool = True) -> None:
        self.flag = flag


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = Cy()
    if c.flag:
        return 1
    return 0

