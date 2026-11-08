r"""Test 1323 — ROUTE #118 second carrier (class scope): a CLASS-BODY rebinding `m = n` was
ignored — `c.m()` was modelled against `m`'s contract (`\result == 1`) while Python runs `n`
and returns 2. The rebinding refusal now covers class bodies (PYCSL-IR-FUNCTION-NAME-REBOUND).
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

    m = n


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.m()
