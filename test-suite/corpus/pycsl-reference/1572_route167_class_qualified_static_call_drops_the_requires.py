r"""Test 1572 - ROUTE #167 (gen #29): `C.get(0)` on a staticmethod declaring `requires d != 0` PROVED the caller (CPython ZeroDivisionError).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    @staticmethod
    #@ requires d != 0
    #@ ensures \result == 1
    def get(d: int) -> int:
        return d // d


#@ ensures \result == 5
def probe() -> int:
    C.get(0)
    return 5
