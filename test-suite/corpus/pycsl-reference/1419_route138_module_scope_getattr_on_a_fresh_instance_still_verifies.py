r"""Test 1419 — ROUTE #138 control: an ordinary module-scope `getattr` on an instance of a class defined in this module has a receiver the file can describe, and still verifies.
"""
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n = 0


c = C()
z = getattr(c, "n")


#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    return 7