r"""Test 4463 -- gen #37 route #335 (expected FAIL): witness i37: subclass `__init__(k)` stores only `self.k`, class attribute `n = 3`; `f(b) == 0` PROVED (CPython 3). REFUSED (PYCSL-R335-INHERITED-INVARIANT-CONSTRUCTION, route #335).
"""
# pycsl-expected: FAIL
#@ class invariant self.n == 0
class B:
    def __init__(self) -> None:
        self.n = 0

class S(B):
    n = 3
    def __init__(self, k: int) -> None:
        self.k = k

#@ ensures \result == 0
def f(b: B) -> int:
    return b.n

if __name__ == "__main__":
    assert f(S(1)) == 0, f(S(1))
