r"""Test 1655 - ROUTE #185 (gen #29): `self.inner.get()` on a guarded `Inner.get` (`requires self.x != 0`) with `x == 0` PROVED `\result == 5` (CPython ZeroDivisionError): route #100's resolution turns the receiver into the key `outer__inner_get`, which names no function, so routes #167/#176 looked up nothing. A key matching no function now falls back to the method-name match.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class Inner:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ requires self.x != 0
    #@ ensures \result == 1
    def get(self) -> int:
        return self.x // self.x


class Outer:
    def __init__(self) -> None:
        self.inner = Inner(0)

    #@ ensures \result == 5
    def run(self) -> int:
        self.inner.get()
        return 5
