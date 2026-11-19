r"""Test 4461 -- gen #37 route #335 (expected FAIL): witness i35: subclass class attribute `n = -1` + `__init__: pass` (base `__init__` never runs); the inherited goal assumed the base's `n = 0` and `f(b) >= 0` PROVED (CPython -1). REFUSED (PYCSL-R335-INHERITED-INVARIANT-CONSTRUCTION, route #335).
"""
# pycsl-expected: FAIL
#@ class invariant self.n >= 0
class B:
    def __init__(self) -> None:
        self.n = 0

class S(B):
    n = -1
    def __init__(self) -> None:
        pass

#@ ensures \result >= 0
def f(b: B) -> int:
    return b.n

if __name__ == "__main__":
    assert f(S()) >= 0, f(S())
