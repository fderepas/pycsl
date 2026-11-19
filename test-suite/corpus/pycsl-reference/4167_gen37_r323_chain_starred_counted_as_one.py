r"""Test 4167 -- gen #37 route #323 (expected FAIL): `len(list(itertools.chain(*xss)))` was modelled as `len(xss)` (CPython 3 for [[1, 2], [3]]). Starred REFUSED.
"""
# pycsl-expected: FAIL
import itertools
from typing import List
#@ requires len(xss) == 2
#@ ensures \result == 2
#@ assigns \nothing
def f(xss: List[List[int]]) -> int:
    return len(list(itertools.chain(*xss)))

if __name__ == "__main__":
    assert f([[1, 2], [3]]) == 2, f([[1, 2], [3]])
