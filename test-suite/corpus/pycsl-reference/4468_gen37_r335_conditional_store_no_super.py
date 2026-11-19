r"""Test 4468 -- gen #37 route #335 (expected FAIL): probe p4: subclass `__init__(k)` stores `self.n = 1` only under `if k > 0`, no `super()`, class attribute `n = -2`; `f(b) >= 0` PROVED (CPython -2 for `S(0)`). REFUSED (PYCSL-R335-INHERITED-INVARIANT-CONSTRUCTION, route #335).
"""
# pycsl-expected: FAIL
#@ class invariant self.n >= 0
class B:
    def __init__(self) -> None:
        self.n = 0

class S(B):
    n = -2
    def __init__(self, k: int) -> None:
        if k > 0:
            self.n = 1

#@ ensures \result >= 0
def f(b: B) -> int:
    return b.n

if __name__ == "__main__":
    assert f(S(0)) >= 0, f(S(0))
