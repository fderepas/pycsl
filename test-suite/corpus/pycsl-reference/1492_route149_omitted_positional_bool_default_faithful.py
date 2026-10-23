r"""Test 1492 - ROUTE #149 (gen #29) positive twin of 1491: `True` binds 1 and `\result == 1` PROVES (FAILS at HEAD).
"""
_ = 0  # anchor


class Cy:
    def __init__(self, flag: bool = True) -> None:
        self.flag = flag


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    c = Cy()
    if c.flag:
        return 1
    return 0

