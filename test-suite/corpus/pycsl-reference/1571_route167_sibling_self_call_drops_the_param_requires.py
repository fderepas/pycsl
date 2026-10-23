r"""Test 1571 - ROUTE #167 (gen #29): `self.get(0)` on a sibling method declaring `requires d != 0` PROVED the caller (CPython ZeroDivisionError).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ requires d != 0
    #@ ensures \result == 1
    def get(self, d: int) -> int:
        return d // d

    #@ ensures \result == 5
    def run(self) -> int:
        self.get(0)
        return 5


#@ ensures \result == 5
def probe() -> int:
    c = C(3)
    return c.run()
