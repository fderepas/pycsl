r"""Test 1348 — ROUTE #125 positive control: the same diamond `D(B, C)`; the TRUE C3 answer `D().m() == 3` PROVES (it did not before the repair — the model gave `A.m`).
"""
# pycsl-expected: PASS
_ = 0  # anchor


class A:
    def __init__(self) -> None:
        self.a = 0

    #@ ensures \result == 1
    #@ assigns \nothing
    def m(self) -> int:
        return 1


class B(A):
    def __init__(self) -> None:
        self.a = 0


class C(A):
    def __init__(self) -> None:
        self.a = 0

    #@ ensures \result == 3
    #@ assigns \nothing
    def m(self) -> int:
        return 3


class D(B, C):
    def __init__(self) -> None:
        self.a = 0


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    d = D()
    return d.m()
