r"""Test 1483 - ROUTE #148/#149 (gen #29): an omitted positional `r: float = 2.5` gave `{ r = 0 }` and `== 0` PROVED; CPython 1. Refused: the default is not an int the model can state, so the field is UNKNOWN.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class Cy:
    def __init__(self, r: float = 2.5) -> None:
        self.r = r


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = Cy()
    if c.r > 2:
        return 1
    return 0

