r"""Test 4816 -- gen #37 route #359 (expected FAIL): witness m15: `class C(B, A): pass` where B binds `m = _bm` (a module function `-> float`, 0.5) and `A.m -> int`; `g(a: A)` with `ensures \result == 0` over `a.m() % 1` PROVED (CPython `g(C())` 0.5). REFUSED (PYCSL-SEM-OVERRIDE-REFINEMENT: the MRO-picked binding is not a top-level def).
"""
# pycsl-expected: FAIL
class A:
    def __init__(self) -> None:
        self.n = 0
    def m(self) -> int:
        return 1

def _bm(self: object) -> float:
    return 0.5

class B:
    def __init__(self) -> None:
        self.n = 0
    m = _bm

class C(B, A):
    pass

#@ ensures \result == 0
def g(a: A) -> int:
    return a.m() % 1


if __name__ == "__main__":
    r = g(C())
    assert r == 0.5, r
