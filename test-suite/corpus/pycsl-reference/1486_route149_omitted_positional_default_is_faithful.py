r"""Test 1486 - ROUTE #149 (gen #29) positive twin of 1477: `Cy()` with `r: int = 5` now PROVES `\result == 1` (FAILS at HEAD).
"""
_ = 0  # anchor


class Cy:
    def __init__(self, r: int = 5) -> None:
        self.r = r


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    c = Cy()
    if c.r > 2:
        return 1
    return 0

