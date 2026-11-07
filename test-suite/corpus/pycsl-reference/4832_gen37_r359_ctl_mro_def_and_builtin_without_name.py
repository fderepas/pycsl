r"""Test 4832 -- gen #37 route #359: CONTROL: `C(B, A)` whose MRO-picked `B.m` is a top-level def refining `A.m` (B also binds an unrelated `k = 3`), and `D(float, A)` where float has no `m`; PROVES (CPython 1, 1, 1).
"""
# pycsl-expected: PASS
class A:
    def __init__(self) -> None:
        self.n = 0
    #@ ensures \result == 1
    def m(self) -> int:
        return 1

class B:
    k = 3
    def __init__(self) -> None:
        self.n = 0
    #@ ensures \result == 1
    def m(self) -> int:
        return 1

class C(B, A):
    pass

class D(float, A):
    pass

#@ ensures \result == 1
def g(a: A) -> int:
    return a.m()


if __name__ == "__main__":
    assert g(A()) == 1
    assert g(C()) == 1
    assert g(D()) == 1
