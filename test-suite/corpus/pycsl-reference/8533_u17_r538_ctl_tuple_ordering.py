r"""Test 8533 -- route #538 (control, expected PASS): the witness's shape with the ordering on the tuples' int COMPONENTS (`t[0] < u[0]` of two `Tuple[int, int]`), which route #538 does not judge; CPython f((1, 2), (2, 1)) returns 1
"""
# pycsl-expected: PASS
from typing import Tuple


#@ no_exception \all
def f(t: Tuple[int, int], u: Tuple[int, int]) -> int:
    return 1 if t[0] < u[0] else 0


if __name__ == "__main__":
    print(f((1, 2), (2, 1)))
