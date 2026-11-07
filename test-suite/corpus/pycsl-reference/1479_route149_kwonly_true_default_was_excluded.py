r"""Test 1479 - ROUTE #149 (gen #29): route #82's constant capture excluded `bool`, so an omitted `*, r: int = True` gave `{ r = 0 }` and `c.r > 0` false PROVED `== 0`; CPython 1. `True` is captured as 1.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class Cy:
    def __init__(self, *, r: int = True) -> None:
        self.r = r


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = Cy()
    if c.r > 0:
        return 1
    return 0

