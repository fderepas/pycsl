r"""Test 4633 -- gen #37 route #344: CONTROL: `class C(B, D): pass` diamond whose MRO-picked `D.m` returns `bool` under `A.m -> int` (`bool` <: `int`): R5 through the MRO admits it; `g(C())` PROVES `\result == 0` (CPython 0).
"""
# pycsl-expected: PASS
class A:
    def __init__(self) -> None:
        self.n = 0
    def m(self) -> int:
        return 1

class B(A):
    pass

class D(A):
    def m(self) -> bool:
        return True

class C(B, D):
    pass

#@ ensures \result == 0
def g(a: A) -> int:
    return a.m() % 1

if __name__ == "__main__":
    assert g(C()) == 0
    assert g(A()) == 0
