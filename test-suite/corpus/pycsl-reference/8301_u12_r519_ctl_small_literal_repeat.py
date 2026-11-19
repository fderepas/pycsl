r"""Test 8301 -- route #519 (control, expected PASS): a constructor whose repetitions have a small literal count (`[0] * 4`, `"ab" * 3`, `(0,) * 2`, `k * 3` over an int parameter) stays a field initialiser; `no_exception \all` over the caller; CPython f(5) returns 1
"""
# pycsl-expected: PASS
from typing import List


class C:
    def __init__(self, k: int) -> None:
        self.xs: List[int] = [0] * 4
        self.s = "ab" * 3
        self.t = (0,) * 2
        self.k = k * 3


#@ no_exception \all
#@ ensures \result == 1
def f(n: int) -> int:
    c = C(n)
    return 1


if __name__ == "__main__":
    print(f(5))
