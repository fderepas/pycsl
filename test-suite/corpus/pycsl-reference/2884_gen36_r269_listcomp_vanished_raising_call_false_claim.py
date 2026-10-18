r"""Test 2884 — route #269 R3 (expected FAIL): `m` declares `#@ no_exception \all` and builds
`[self.chk(x) for x in xs]`, where `chk` raises ValueError for `k > 0` (a declared `#@
raises`). The comprehension is lowered opaquely, the call — and its exception — vanished,
so the claim PROVED at 8b0bfbbd. CPython: `m([1])` raises ValueError. Now refused
(PYCSL-SEM-VANISHED-CALL-EFFECT).
"""
# pycsl-expected: FAIL
from typing import List

class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == 0
    #@ assigns \nothing
    #@ raises ValueError when k > 0
    def chk(self, k: int) -> int:
        if k > 0:
            raise ValueError("bad")
        return 0

    #@ ensures \result == 7
    #@ assigns \nothing
    #@ no_exception \all
    def m(self, xs: List[int]) -> int:
        ys = [self.chk(x) for x in xs]
        return 7

if __name__ == "__main__":
    try:
        print(C().m([1]))
    except ValueError:
        print("ValueError")
