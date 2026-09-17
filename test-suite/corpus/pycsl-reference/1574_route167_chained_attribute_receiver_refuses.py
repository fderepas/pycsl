r"""Test 1574 - ROUTE #167 carrier (gen #29): `h.c.sget()` - a receiver whose class the call site does not resolve - on a method declaring `requires self.x != 0` PROVED `\result == 5` (CPython ZeroDivisionError). The callee is matched by method name and, with no nameable receiver, the call site asserts false.
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


class H:
    def __init__(self) -> None:
        self.c = C(0)


#@ ensures \result == 5
def probe() -> int:
    h = H()
    h.c.sget()
    return 5
