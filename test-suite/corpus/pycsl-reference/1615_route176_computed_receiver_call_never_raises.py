r"""Test 1615 - ROUTE #176 carrier (gen #29): `C().go(-1)` - a computed receiver - with `go` raising ValueError, caught by the caller, PROVED `\result == 0` on the #176 draft (CPython 9).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.k = 0

    def go(self, v: int) -> int:
        if v < 0:
            raise ValueError()
        return v


#@ ensures \result == 0
def probe() -> int:
    try:
        C().go(-1)
    except ValueError:
        return 9
    return 0
