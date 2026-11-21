r"""Test 1325 — ROUTE #119 (order 2, carrier = route #118's landed refusal): a module-level ATTRIBUTE store `C.m = C.n` rebinds the method with no Name binding, and `c.m()` PROVED `\result == 1` while CPython returns 2. Refused (PYCSL rebinding refusal, now in Module3_Weaver.process).
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


C.m = C.n


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.m()
