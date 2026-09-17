r"""Test 1575 - ROUTE #168 (gen #29): `_g.sget()` in statement position on a module-global instance `_g = C(0)`, with `sget` declaring `requires self.x != 0` and returning `self.x // self.x`, PROVED `\result == 5`: the global-method inliner popped the tail `return` and threw its expression away, division included (CPython ZeroDivisionError). The discarded value is now evaluated into a fresh local.
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


_g = C(0)


#@ ensures \result == 5
def probe() -> int:
    _g.sget()
    return 5


