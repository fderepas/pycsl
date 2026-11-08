r"""Test 1333 — ROUTE #120: a `__getattribute__` that redirects `m` to `n` was never consulted; `C().m()` PROVED `m`s contract `\result == 1` while CPython returns 2. Classes defining attribute-access hooks are refused.
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.a = 0

    def __getattribute__(self, name):
        if name == "m":
            name = "n"
        return object.__getattribute__(self, name)

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
