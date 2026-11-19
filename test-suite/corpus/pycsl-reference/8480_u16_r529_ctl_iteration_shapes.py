r"""Test 8480 -- routes #529-#539 (control, expected PASS): iteration and unpacking at KNOWN shapes stay field initialisers under the kind-flow judge: `for x in xs` / a comprehension over a List[int], `a, b = t` of a Tuple[int, int], `range(0, n, 2)` (literal step), `zip(xs, ys)` without strict, `for i, x in enumerate(xs)`; CPython f([1, 2], [3], (4, 5), 3) returns 1
"""
# pycsl-expected: PASS
from typing import List, Tuple


class C:
    def __init__(self, xs: List[int], ys: List[int], t: Tuple[int, int], n: int) -> None:
        self.k = 0
        for x in xs:
            self.k = 1
        a, b = t
        self.a = a
        self.sq = [x * 2 for x in xs]
        self.ev = [i for i in range(0, n, 2)]
        self.pairs = list(zip(xs, ys))
        for i, x in enumerate(xs):
            self.last = i


#@ no_exception \all
#@ ensures \result == 1
def f(xs: List[int], ys: List[int], t: Tuple[int, int], n: int) -> int:
    c = C(xs, ys, t, n)
    return 1


if __name__ == "__main__":
    print(f([1, 2], [3], (4, 5), 3))
