r"""Test 2891 — route #269 R3 (expected FAIL): `m` declares `#@ no_exception \all` and builds
`[self.inv(x) for x in xs]`, where `inv` REQUIRES `k > 0` over `10 // k`. The comprehension
is lowered opaquely, so the call's precondition is never checked and the implicit
ZeroDivisionError behind it vanished: PROVED at 8b0bfbbd. CPython: `m([0])` raises
ZeroDivisionError. A vanished call to a callee with a precondition is now refused
(PYCSL-SEM-VANISHED-CALL-EFFECT).
"""
# pycsl-expected: FAIL
from typing import List

class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ requires k > 0
    #@ ensures \result == 10 // k
    #@ assigns \nothing
    def inv(self, k: int) -> int:
        return 10 // k

    #@ ensures \result == 7
    #@ assigns \nothing
    #@ no_exception \all
    def m(self, xs: List[int]) -> int:
        ys = [self.inv(x) for x in xs]
        return 7

if __name__ == "__main__":
    try:
        print(C().m([0]))
    except ZeroDivisionError:
        print("ZeroDivisionError")
