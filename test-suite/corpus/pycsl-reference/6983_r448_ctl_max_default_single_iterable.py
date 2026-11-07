r"""Test 6983 -- route #448 (expected PASS): CONTROL: `max(a, b)` / `min(a, b)` with two positionals and no `default=`, and `len` / `abs` calls that bind their real signatures, in an unclaimed helper and under `#@ no_exception \all`. Admitted; PROVED at base and candidate (CPython ok).
"""
# pycsl-expected: PASS
from typing import List


#@ ensures \result >= 0
def h(xs: List[int]) -> int:
    return len(xs)


#@ no_exception \all
#@ ensures \result >= a and \result >= b
def f(a: int, b: int, xs: List[int]) -> int:
    return max(a, b) + 0 * min(a, b) + 0 * h(xs) + 0 * abs(a)


if __name__ == "__main__":
    print(f(1, 2, [1]))
