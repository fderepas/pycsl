r"""Test 1485 - ROUTE #148 (gen #29): `self.r = 1; self.r = 2.5` - route #88's last-wins arm truncated the same way; `== 0` PROVED, CPython 1. Refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class Cy:
    def __init__(self) -> None:
        self.r = 1
        self.r = 2.5


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = Cy()
    if c.r > 2:
        return 1
    return 0

