r"""Test 4152 -- gen #37 route #321 (expected FAIL): `OrderedDict(d)` before and after `d[1] = 9` shared one constant (CPython 0 vs 9). Non-literal seed REFUSED.
"""
# pycsl-expected: FAIL
from collections import OrderedDict
from typing import Dict

#@ ensures \result == 0
#@ assigns \nothing
def g(d: Dict[int, int]) -> int:
    a: Dict[int, int] = OrderedDict(d)
    d[1] = 9
    b: Dict[int, int] = OrderedDict(d)
    if a.get(1, 0) != b.get(1, 0):
        return 1
    return 0

if __name__ == "__main__":
    assert g({}) == 0, g({})
