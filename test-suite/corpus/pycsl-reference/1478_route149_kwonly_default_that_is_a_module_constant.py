r"""Test 1478 - ROUTE #149 (gen #29, deferral-audit on route #82's own comment "a non-constant default stays omitted and is route #79's class" - no route #79 arm reads parameter defaults): `*, r: int = K` with `K = 5`, `Cy()` gave `{ r = 0 }` and `== 0` PROVED; CPython 1. The field is now UNKNOWN when the argument is omitted.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
K = 5


class Cy:
    def __init__(self, *, r: int = K) -> None:
        self.r = r


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = Cy()
    if c.r > 2:
        return 1
    return 0

