r"""Test 4465 -- gen #37 route #335 (expected FAIL): probe p1: `class S(M, B)` where `M.__init__` calls `super().__init__()` (cooperatively reaching `B.__init__`) and THEN stores `n = -1`; the merged default took B's `0` and `f(b) >= 0` PROVED (CPython -1). REFUSED (PYCSL-R335-INHERITED-INVARIANT-CONSTRUCTION, route #335).
"""
# pycsl-expected: FAIL
class M:
    def __init__(self) -> None:
        super().__init__()
        self.n = -1

#@ class invariant self.n >= 0
class B:
    def __init__(self) -> None:
        self.n = 0

class S(M, B):
    pass

#@ ensures \result >= 0
def f(b: B) -> int:
    return b.n

if __name__ == "__main__":
    assert f(S()) >= 0, f(S())
