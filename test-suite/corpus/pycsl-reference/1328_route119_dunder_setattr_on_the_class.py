r"""Test 1328 — ROUTE #119: `type.__setattr__(C, "m", C.n)`, the dunder spelling of setattr. `c.m()` PROVED `\result == 1`, CPython 2. Refused.
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.a = 0

    #@ ensures \result == 1
    #@ assigns \nothing
    def m(self) -> int:
        return 1

    #@ ensures \result == 2
    #@ assigns \nothing
    def n(self) -> int:
        return 2


type.__setattr__(C, "m", C.n)


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.m()
