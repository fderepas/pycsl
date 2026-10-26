r"""Test 5358 -- gen #37 route #382 (expected FAIL): `ys = [1]; {ys}` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from typing import List, Dict, Set

#@ no_exception \all
#@ ensures \result == 1
def g(xs: List[int]) -> int:
    ys = [1]
    s = {ys}
    return 1

if __name__ == "__main__":
    print(g([1]))
