r"""Test 10158 -- run #8 lvW typed tuple-return exception MUTANT (expected FAIL): 10157 with the recursive step mutated to `t[0] + 2`; `\result[0] == n` is FALSE of the program (CPython: r(3) == (6, "z")) and must not prove.
"""
# pycsl-expected: FAIL
from typing import Tuple

#@ requires n >= 0
#@ ensures \result[0] == n
#@ \variant n
def r(n: int) -> Tuple[int, str]:
    if n == 0:
        return 0, "z"
    t = r(n - 1)
    return t[0] + 2, t[1]


if __name__ == "__main__":
    print(r(0), r(3))
