r"""Test 4462 -- gen #37 route #335 (expected FAIL): witness i36: subclass `__init__` stores only `self.m`; `self.n` is never stored, yet `no_exception \all` + `f(b) >= 0` PROVED (CPython AttributeError). REFUSED (PYCSL-R335-INHERITED-INVARIANT-CONSTRUCTION, route #335).
"""
# pycsl-expected: FAIL
#@ class invariant self.n >= 0
class B:
    def __init__(self) -> None:
        self.n = 0

class S(B):
    def __init__(self) -> None:
        self.m = 1

#@ no_exception \all
#@ ensures \result >= 0
def f(b: B) -> int:
    return b.n

if __name__ == "__main__":
    assert f(S()) >= 0, f(S())
