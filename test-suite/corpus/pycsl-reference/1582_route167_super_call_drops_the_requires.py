r"""Test 1582 - ROUTE #167 carrier (gen #29): `super().sget()` in an override, and `D(0).sget()` on the subclass, with the base `sget` declaring `requires self.x != 0`: PROVED `\result == 5` (CPython ZeroDivisionError).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ requires self.x != 0
    #@ ensures \result == 1
    def sget(self) -> int:
        return self.x // self.x

    #@ requires d != 0
    #@ ensures \result == 1
    def get(self, d: int) -> int:
        return d // d


class D(C):
    def sget(self) -> int:
        super().sget()
        return 1


#@ ensures \result == 5
def probe() -> int:
    D(0).sget()
    return 5
