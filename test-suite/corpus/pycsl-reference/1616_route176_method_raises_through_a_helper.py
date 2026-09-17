r"""Test 1616 - ROUTE #176 carrier (gen #29): `go` raises only through a helper `self.check(v)`; `c.go(-1)` caught by the caller PROVED `\result == 0` on the #176 draft (CPython 9). Escaping exceptions are now computed transitively.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.k = 0

    def check(self, v: int) -> None:
        if v < 0:
            raise ValueError()

    def go(self, v: int) -> int:
        self.check(v)
        return v


#@ ensures \result == 0
def probe() -> int:
    c = C()
    try:
        c.go(-1)
    except ValueError:
        return 9
    return 0
