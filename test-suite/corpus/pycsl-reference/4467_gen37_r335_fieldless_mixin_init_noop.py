r"""Test 4467 -- gen #37 route #335 (expected FAIL): probe p3: a FIELDLESS mixin `M` with `__init__: pass` first in `class S(M, B)` (class attribute `n = -1`); B's constructor never runs and `f(b) >= 0` PROVED (CPython -1). REFUSED (PYCSL-R335-INHERITED-INVARIANT-CONSTRUCTION, route #335).
"""
# pycsl-expected: FAIL
class M:
    def __init__(self) -> None:
        pass

#@ class invariant self.n >= 0
class B:
    def __init__(self) -> None:
        self.n = 0

class S(M, B):
    n = -1

#@ ensures \result >= 0
def f(b: B) -> int:
    return b.n

if __name__ == "__main__":
    assert f(S()) >= 0, f(S())
