r"""Test 4466 -- gen #37 route #335 (expected FAIL): probe p2: the SUBCLASS's own invariant `self.n >= 5` over a base field its `__init__: pass` never stores (class attribute `n = 1`); the goal assumed the base's `n = 5` and `g(s) >= 5` PROVED (CPython 1). REFUSED (PYCSL-R335-INHERITED-INVARIANT-CONSTRUCTION, route #335).
"""
# pycsl-expected: FAIL
class B:
    def __init__(self) -> None:
        self.n = 5

#@ class invariant self.n >= 5
class S(B):
    n = 1
    def __init__(self) -> None:
        pass

#@ ensures \result >= 5
def g(s: S) -> int:
    return s.n

if __name__ == "__main__":
    assert g(S()) >= 5, g(S())
