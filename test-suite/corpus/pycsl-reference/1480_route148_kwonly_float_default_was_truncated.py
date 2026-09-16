r"""Test 1480 - ROUTE #148 (gen #29): an omitted `*, r: float = 2.5` was captured as `int(2.5)` = 2, so `c.r > 2` was false and `== 0` PROVED; CPython 1. A non-integral float default makes the field UNKNOWN.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class Cy:
    def __init__(self, *, r: float = 2.5) -> None:
        self.r = r


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = Cy()
    if c.r > 2:
        return 1
    return 0

