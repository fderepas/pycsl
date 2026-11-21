r"""Test 1335 — ROUTE #119 (instance level): `self.m = abs` in `__init__` shadows the method `m`; `c.m(-3)` PROVED the method contract `\result == -2` while CPython calls `abs` and returns 3. A builtin value slipped past the function-as-value error that fenced `self.m = fn`. Refused.
"""
# pycsl-expected: FAIL
class C:
    #@ assigns self.a
    def __init__(self) -> None:
        self.a = 0
        self.m = abs

    #@ ensures \result == y + 1
    #@ assigns \nothing
    def m(self, y: int) -> int:
        return y + 1


#@ ensures \result == -2
def f() -> int:
    c = C()
    return c.m(-3)
