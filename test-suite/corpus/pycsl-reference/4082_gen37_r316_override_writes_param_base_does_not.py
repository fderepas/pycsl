r"""Test 4082 -- gen #37 route #316 (expected FAIL): override `S.m` writes `xs`, base `B.m` does not; `h(b)` through the base stub PROVED `ys[0] == 0` (CPython 5). REFUSED: PYCSL-OVERRIDE-FRAME.
"""
# pycsl-expected: FAIL
from typing import List
class B:
    def __init__(self) -> None:
        self.n = 0
    def m(self, xs: List[int]) -> None:
        pass

class S(B):
    def m(self, xs: List[int]) -> None:
        if len(xs) > 0:
            xs[0] = 5

#@ ensures \result == 0
def h(b: B) -> int:
    ys = [0]
    b.m(ys)
    return ys[0]

if __name__ == "__main__":
    assert h(S()) == 0, h(S())
