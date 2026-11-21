r"""Test 6785 -- route #443 (expected PASS): CONTROL -- an element of `List[C]` for a file class `C` as a method receiver; PROVED at base and candidate.
ROUTE #506 (run #4): now expected FAIL -- REFUSED PYCSL-R506-TRIGGER-SITE-UNLOWERED by design. The subscript sits in a position the lowering never evaluates, so the IndexError / KeyError obligation the `no_exception \all` claim covers is absent from the VC; the program is CPython-honest only because of its guard / data, which the model never checks (`xs[0].size()` lowers without its receiver (`size_0 ()`): twin 8019 PROVED at base, CPython IndexError).
"""
# pycsl-expected: FAIL
from typing import List


class C:
    def __init__(self, n: int) -> None:
        self.n = n

    #@ no_exception \all
    def size(self) -> int:
        return 1


#@ no_exception \all
def f(xs: List[C]) -> int:
    if len(xs) == 0:
        return 0
    return xs[0].size()


if __name__ == "__main__":
    print("result", f([C(1)]))
