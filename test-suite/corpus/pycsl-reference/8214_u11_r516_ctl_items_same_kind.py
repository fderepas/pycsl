r"""Test 8214 -- route #516 (control, expected PASS): `for k, v in d.items()` over a `Dict[int, int]` reads both targets as ints (from the declared key / value types), so `k * v` and `k + v` are int arithmetic with no promotion or repetition; CPython f({2: 3}) returns 1
"""
# pycsl-expected: PASS
from typing import Dict


#@ no_exception \all
#@ ensures \result == 1
def f(d: Dict[int, int]) -> int:
    for k, v in d.items():
        w = k * v
        u = k + v
    return 1


if __name__ == "__main__":
    print(f({2: 3}))
