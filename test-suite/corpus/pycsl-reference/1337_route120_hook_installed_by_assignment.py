r"""Test 1337 — ROUTE #120: an attribute-access hook installed by class-body ASSIGNMENT (`__getattribute__ = _redirect`) is the same hook; it was refused before only by incidental Why3 errors. Refused structurally.
"""
# pycsl-expected: FAIL
def _redirect(self, name: str):
    if name == "m":
        name = "n"
    return object.__getattribute__(self, name)


class C:
    __getattribute__ = _redirect

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


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.m()
