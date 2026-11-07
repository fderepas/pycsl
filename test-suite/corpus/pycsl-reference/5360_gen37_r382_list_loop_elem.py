r"""Test 5360 -- gen #37 route #382 (expected FAIL): `for y in xs: {y}` over `List[List[int]]` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from typing import List, Dict, Set

#@ no_exception \all
#@ ensures \result == 1
def g(xs: List[List[int]]) -> int:
    for y in xs:
        s = {y}
    return 1

if __name__ == "__main__":
    print(g([[1]]))
