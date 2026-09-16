r"""Test 1477 - ROUTE #149 (gen #29): `def __init__(self, r: int = 5)` with `Cy()` - the IR carried no positional parameter defaults and a zero-argument call never entered the binding block, so the record literal was `{ r = 0 }` and `\result == 0` PROVED while CPython returns 1 (5 > 2). The positional twin of route #82.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class Cy:
    def __init__(self, r: int = 5) -> None:
        self.r = r


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = Cy()
    if c.r > 2:
        return 1
    return 0

