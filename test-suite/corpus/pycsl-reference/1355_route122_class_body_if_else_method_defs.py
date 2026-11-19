r"""Test 1355 — ROUTE #122 (class-body arm, carrier of the first repair draft): two defs of method `m` in the arms of an `if` inside the CLASS BODY; the model kept the textually last (`1`) and PROVED `C().m() == 1` while CPython takes the if arm and returns 2. The compound-statement check now runs in every class body as well as the module.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
FLAG = 1


class C:
    def __init__(self) -> None:
        self.a = 0

    if FLAG == 1:
        #@ ensures \result == 2
        #@ assigns \nothing
        def m(self) -> int:
            return 2
    else:
        #@ ensures \result == 1
        #@ assigns \nothing
        def m(self) -> int:
            return 1


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.m()
