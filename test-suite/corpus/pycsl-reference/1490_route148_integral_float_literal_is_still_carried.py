r"""Test 1490 - ROUTE #148 control (gen #29): an INTEGRAL float `self.r = 2.0` is still carried as 2 and `c.r > 1` PROVES `== 1` on both sides of the repair.
"""
_ = 0  # anchor


class Cy:
    def __init__(self) -> None:
        self.r = 2.0


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    c = Cy()
    if c.r > 1:
        return 1
    return 0

