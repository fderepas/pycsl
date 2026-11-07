r"""Test 2889 — route #269 R3 (expected PASS; FAILED at 8b0bfbbd): 2882 with the caller
HONESTLY marked `#@ \diverges`. The opaque comprehension's lost call is now represented by an
opaque diverging application, so Why3 accepts the clause (before: "this expression does
not diverge"). CPython: `m([0])` returns 7; `m([1])` never returns.
"""
from typing import List

class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == 0
    #@ assigns \nothing
    #@ \diverges
    def spin(self, k: int) -> int:
        while k > 0:
            k = k + 1
        return 0

    #@ ensures \result == 7
    #@ assigns \nothing
    #@ \diverges
    def m(self, xs: List[int]) -> int:
        ys = [self.spin(x) for x in xs]
        return 7

if __name__ == "__main__":
    print(C().m([0]))
