r"""Test 5353 -- gen #37 route #382 (expected FAIL): `d: MutableSet[int]`, `{d}` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from typing import MutableSet

#@ no_exception \all
#@ ensures \result == 1
def g(d: MutableSet[int]) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(set()))
