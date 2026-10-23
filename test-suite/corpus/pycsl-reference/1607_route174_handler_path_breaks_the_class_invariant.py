r"""Test 1607 - ROUTE #174 carrier (gen #29): a method with no `ensures` whose `except ValueError` path (around `int(s)`) sets `self.x = -1` under `class invariant self.x >= 0`; a caller`s `c.m("1.5"); return c.x` PROVED `\result >= 0` (CPython -1). A class invariant is a claim: such methods are now widened / checked like claiming functions.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ class invariant self.x >= 0
class C:
    def __init__(self) -> None:
        self.x = 0

    #@ assigns self.x
    def m(self, s: str) -> None:
        try:
            v = int(s)
            self.x = 1
        except ValueError:
            self.x = -1


#@ ensures \result >= 0
def probe() -> int:
    c = C()
    c.m("1.5")
    return c.x
