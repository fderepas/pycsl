r"""Test 5681 -- gen #37 CONTROL routes #396 / #397 (expected PASS): no class of `R`'s subclass closure binds `k` (`S(R)` binds `j` only), so `getattr(r, "k", 0) == 0` is the faithful default; PROVED (CPython 0).
"""
# pycsl-expected: PASS
class R:
    def __init__(self) -> None:
        self.x: int = 1
class S(R):
    def __init__(self) -> None:
        super().__init__()
        self.j: int = 5
#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "k", 0)
if __name__ == "__main__":
    assert f(S()) == 0 and f(R()) == 0
