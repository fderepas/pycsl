r"""Test 10157 -- run #8 lvW typed tuple-return exception (expected PASS): a RECURSIVE `Tuple[int, str]` function whose base case is an early `Return_tup_int_string` raise; `\result[0] == n` proves through the recursive call's typed result. Twin: 10158 (expected FAIL).
"""
# pycsl-expected: PASS
from typing import Tuple

#@ requires n >= 0
#@ ensures \result[0] == n
#@ \variant n
def r(n: int) -> Tuple[int, str]:
    if n == 0:
        return 0, "z"
    t = r(n - 1)
    return t[0] + 1, t[1]


if __name__ == "__main__":
    print(r(0), r(3))
