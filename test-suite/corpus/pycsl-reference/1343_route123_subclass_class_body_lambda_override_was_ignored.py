r"""Test 1343 — ROUTE #123: `class B(A): m = lambda self: 2` overrides the inherited `A.m`, but inheritance cloned `A.m` onto `B` and `B().m()` PROVED `\result == 1` while CPython returns 2. The clone is now skipped (fail-closed: the call has no inherited contract).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class A:
    def __init__(self) -> None:
        self.a = 0

    #@ ensures \result == 1
    #@ assigns \nothing
    def m(self) -> int:
        return 1


class B(A):
    m = lambda self: 2

    def __init__(self) -> None:
        self.a = 0


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    b = B()
    return b.m()
