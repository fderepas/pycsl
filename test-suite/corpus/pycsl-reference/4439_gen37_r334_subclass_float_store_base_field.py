r"""Test 4439 -- gen #37 route #334 (expected FAIL): a SUBCLASS store to an inherited field (`B.__init__` sets `self.r = 0`; `S(B).__init__` calls `super().__init__()` then `self.r = 0.5`) did not taint the BASE field label, so `g(b: B)` with `b.r % 1 == 0` PROVED (CPython False for `g(S())`). REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK): a receiver typed as the base may hold the subclass, so every descendant store counts.
"""
# pycsl-expected: FAIL
class B:
    def __init__(self) -> None:
        self.r = 0

class S(B):
    def __init__(self) -> None:
        super().__init__()
        self.r = 0.5

#@ ensures \result == True
def g(b: B) -> bool:
    return b.r % 1 == 0

if __name__ == "__main__":
    assert g(S()) == True, g(S())
