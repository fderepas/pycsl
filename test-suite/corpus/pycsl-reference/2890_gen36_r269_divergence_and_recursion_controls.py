r"""Test 2890 — route #269 CONTROL (expected PASS): what the repair must NOT touch.
(a) a comprehension over a TERMINATING, non-raising method (`[self.dbl(x) for x in xs]`);
(b) `#@ \diverges` + `#@ no_exception \all` on a LOOP that is not a recursion (no
RecursionError possible); (c) a TERMINATING recursion with a `#@ \variant` under
`#@ no_exception \all` (RecursionError for a deep `n` is the documented scope of `\all`, not
a divergence). CPython: 7 0 0.
"""
from typing import List

class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == 2 * k
    #@ assigns \nothing
    def dbl(self, k: int) -> int:
        return 2 * k

    #@ ensures \result == 7
    #@ assigns \nothing
    def m(self, xs: List[int]) -> int:
        ys = [self.dbl(x) for x in xs]
        return 7

#@ requires k <= 0
#@ ensures \result == 0
#@ assigns \nothing
#@ \diverges
#@ no_exception \all
def spin(k: int) -> int:
    while k > 0:
        k = k + 1
    return 0

#@ requires n >= 0
#@ ensures \result == 0
#@ assigns \nothing
#@ \variant n
#@ no_exception \all
def down(n: int) -> int:
    if n == 0:
        return 0
    return down(n - 1)

if __name__ == "__main__":
    print(C().m([1, 2]), spin(0), down(5))
