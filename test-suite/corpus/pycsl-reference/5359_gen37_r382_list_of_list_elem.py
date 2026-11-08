r"""Test 5359 -- gen #37 route #382 (expected FAIL): `xs: List[List[int]]`, `{xs[0]}` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from typing import List, Dict, Set

#@ no_exception \all
#@ ensures \result == 1
def g(xs: List[List[int]]) -> int:
    s = {xs[0]}
    return 1

if __name__ == "__main__":
    print(g([[1]]))
