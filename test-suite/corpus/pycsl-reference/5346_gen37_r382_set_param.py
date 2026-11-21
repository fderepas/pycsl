r"""Test 5346 -- gen #37 route #382 (expected FAIL): `d: Set[int]`, `{d}` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from typing import Set

#@ no_exception \all
#@ ensures \result == 1
def g(d: Set[int]) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(set()))
