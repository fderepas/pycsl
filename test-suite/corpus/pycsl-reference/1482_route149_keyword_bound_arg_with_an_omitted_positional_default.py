r"""Test 1482 - ROUTE #149 (gen #29): `Cy(r=9)` binds `r` by keyword and omits `q: int = 1`; the model gave `q` the witness 0 and `c.r - c.q + 1 - 4 == 6` PROVED; CPython 5.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class Cy:
    def __init__(self, q: int = 1, r: int = 5) -> None:
        self.q = q
        self.r = r


#@ ensures \result == 6
#@ assigns \nothing
def probe() -> int:
    c = Cy(r=9)
    return c.r - c.q + 1 - 4
