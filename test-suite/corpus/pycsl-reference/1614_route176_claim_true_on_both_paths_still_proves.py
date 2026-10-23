r"""Test 1614 - ROUTE #176 control (gen #29): with the stubbed call able to raise, a claim true on both paths (`\result == 3 or \result == 9`) still proves.
"""
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.k = 0

    #@ requires v >= 0
    #@ ensures \result == v
    def go(self, v: int) -> int:
        if v < 0:
            raise ValueError()
        return v


#@ ensures \result == 3 or \result == 9
def probe() -> int:
    c = C()
    try:
        r = c.go(3)
    except ValueError:
        return 9
    return 3
