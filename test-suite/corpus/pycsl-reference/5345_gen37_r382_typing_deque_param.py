r"""Test 5345 -- gen #37 route #382 (expected FAIL): `d: Deque[int]`, `{d}` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from typing import Deque
from collections import deque

#@ no_exception \all
#@ ensures \result == 1
def g(d: Deque[int]) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(deque()))
