r"""Test 8303 -- route #519 (control, expected PASS): `len` / `sorted` / `sum` / `list` of a `List[int]` parameter and a `for` over `range(n)` in a constructor stay field initialisers (a declared list never holds a `range`; a `range` iterated is never sized); CPython f([3, 1], 2) returns 1
"""
# pycsl-expected: PASS
from typing import List


class C:
    def __init__(self, xs: List[int], n: int) -> None:
        self.size = len(xs)
        self.order = sorted(xs)
        self.total = sum(xs)
        self.copy = list(xs)
        self.k = 0
        for i in range(n):
            self.k += 1


#@ no_exception \all
#@ ensures \result == 1
def f(xs: List[int], n: int) -> int:
    c = C(xs, n)
    return 1


if __name__ == "__main__":
    print(f([3, 1], 2))
