r"""Test 1611 - ROUTE #176 (gen #29): `c.go(-1)` with `go` raising ValueError on a negative argument, inside `try ... except ValueError: return 9`, PROVED `\result == 0` (CPython 9): the stubbed method call carries no `raises`, so the handler was dead. When the resolved callee can let E escape and the caller handles E, the call may now raise E first.
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
    c = C()
    try:
        c.go(-1)
    except ValueError:
        return 9
    return 0
