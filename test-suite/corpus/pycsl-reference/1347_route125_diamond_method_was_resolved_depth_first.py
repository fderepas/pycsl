r"""Test 1347 — ROUTE #125: diamond `D(B, C)` over `A` with `C.m` overriding `A.m`. Python's C3 MRO is D, B, C, A, so `D().m()` returns 3; inheritance walked the first base depth-first, cloned `A.m`, and PROVED `\result == 1`. Clones now follow the C3 provider.
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


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    d = D()
    return d.m()
