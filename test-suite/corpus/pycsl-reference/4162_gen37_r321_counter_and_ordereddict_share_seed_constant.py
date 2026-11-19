r"""Test 4162 -- gen #37 route #321 (expected FAIL): `Counter([(1, 1)])` counts the PAIR, `OrderedDict([(1, 1)])` maps 1 to 1, but both were the same constant: `a[1] == b[1]` PROVED (CPython 0 vs 1). Counter is now keyed apart: FAILS.
"""
# pycsl-expected: FAIL
from typing import Dict
from collections import Counter, OrderedDict
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    a: Dict[int, int] = Counter([(1, 1)])
    b: Dict[int, int] = OrderedDict([(1, 1)])
    if a[1] == b[1]:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
