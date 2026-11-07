r"""Test 1569 - ROUTE #167 (gen #29): `c = C(0); c.get(); return 5` with `get` declaring `requires self.x != 0` (body `self.x // self.x`) PROVED `\result == 5` - the call lowered to an abstract stub carrying no precondition - while CPython raises ZeroDivisionError. A stubbed call to a same-file method with a precondition now asserts false.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ requires self.x != 0
    #@ ensures \result == 1
    def get(self) -> int:
        return self.x // self.x


#@ ensures \result == 5
def probe() -> int:
    c = C(0)
    c.get()
    return 5
