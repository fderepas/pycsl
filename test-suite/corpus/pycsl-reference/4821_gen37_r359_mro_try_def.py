r"""Test 4821 -- gen #37 route #359 (expected FAIL): witness m21: as 4816 with `B.m` a `def ... -> float` inside `try:`; PROVED (CPython 0.5). REFUSED (PYCSL-SEM-OVERRIDE-REFINEMENT).
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
    try:
        def m(self) -> float:
            return 0.5
    except Exception:
        pass

class C(B, A):
    pass

#@ ensures \result == 0
def g(a: A) -> int:
    return a.m() % 1


if __name__ == "__main__":
    r = g(C())
    assert r == 0.5, r
