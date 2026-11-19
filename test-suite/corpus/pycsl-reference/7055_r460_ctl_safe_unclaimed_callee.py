r"""Test 7055 -- route #460 (expected PASS): CONTROL -- an un-claimed `g` with no raising site (arithmetic, `len`) and an un-claimed method, reached from `f` claiming `#@ no_exception \all`; PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import List


class Acc:
    def __init__(self) -> None:
        self.total = 0

    def take(self, n: int) -> int:
        return n + 1


def g(xs: List[int], n: int) -> int:
    if 0 <= n:
        return n + len(xs)
    return len(xs)


#@ no_exception \all
def f(xs: List[int], n: int) -> int:
    a = Acc()
    return g(xs, n) + a.take(n)


if __name__ == "__main__":
    print(f([1, 2, 3], 1))
