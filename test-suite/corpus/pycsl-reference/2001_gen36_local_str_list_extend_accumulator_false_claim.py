r"""Test 2001 — gen #36 (expected FAIL): NON-VACUITY twin of 2000 — BOTH extends grow
the accumulator, so `\result == 2` (one extend dropped) must NOT prove.
"""
# pycsl-expected: FAIL
from typing import List


class Collector:
    def __init__(self) -> None:
        self.n = 0

    #@ \trusted
    #@ ensures len(\result) == 2
    #@ assigns \nothing
    def norm(self, xs: List[str]) -> List[str]:
        return ["x", "y"]

    #@ ensures \result == 2
    #@ assigns \nothing
    def gather(self, xs: List[str], ys: List[str]) -> int:
        acc: List[str] = []
        acc.extend(self.norm(xs))
        acc.extend(self.norm(ys))
        if acc:
            return len(acc)
        return 0
