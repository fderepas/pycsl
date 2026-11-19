r"""Test 1581 - ROUTE #167 carrier (gen #29): `C(0).sget()` - a method call on a COMPUTED receiver - reaches the generic unannotated-call fallback with a bare method name, bypassing the stubbed-call precondition assert; with `sget` declaring `requires self.x != 0` it PROVED `\result == 5` (CPython ZeroDivisionError). The fallback now asserts false when a same-file method of that name has a precondition.
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


#@ ensures \result == 5
def probe() -> int:
    C(0).sget()
    return 5
