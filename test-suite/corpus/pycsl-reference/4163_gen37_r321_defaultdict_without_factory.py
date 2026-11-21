r"""Test 4163 -- gen #37 route #321 (expected FAIL): `defaultdict()` has no factory and RAISES KeyError on a missing key; it answered 0 and `d[5] == 0` PROVED. REFUSED.
"""
# pycsl-expected: FAIL
from typing import Dict
from collections import defaultdict
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = defaultdict()
    if d[5] == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
