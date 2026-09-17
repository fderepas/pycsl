r"""Test 1570 - ROUTE #167 (gen #29): the same violated `requires self.x != 0` through a `c: C` parameter receiver PROVED (CPython ZeroDivisionError).
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
def use(c: C) -> int:
    c.get()
    return 5


#@ ensures \result == 5
def probe() -> int:
    return use(C(0))
