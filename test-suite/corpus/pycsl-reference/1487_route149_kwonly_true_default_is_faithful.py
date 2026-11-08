r"""Test 1487 - ROUTE #149 (gen #29) positive twin of 1479: the omitted `*, r: int = True` binds 1 and `\result == 1` PROVES (FAILS at HEAD).
"""
_ = 0  # anchor


class Cy:
    def __init__(self, *, r: int = True) -> None:
        self.r = r


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    c = Cy()
    if c.r > 0:
        return 1
    return 0

