r"""Test 4623 -- gen #37 route #344 (expected FAIL): witness c01: `class C(B, A): pass`, `A.m -> int`, `B.m -> float` (0.5); `g(a: A)` with `ensures \result == 0` over `a.m() % 1` PROVED (CPython `g(C())` 0.5). REFUSED (PYCSL-SEM-OVERRIDE-REFINEMENT: R5 resolves C's inherited def through the C3 MRO).
"""
# pycsl-expected: FAIL
class A:
    def __init__(self) -> None:
        self.n = 0
    def m(self) -> int:
        return 1

class B:
    def __init__(self) -> None:
        self.n = 0
    def m(self) -> float:
        return 0.5

class C(B, A):
    pass

#@ ensures \result == 0
def g(a: A) -> int:
    return a.m() % 1

if __name__ == "__main__":
    assert g(C()) == 0.5
