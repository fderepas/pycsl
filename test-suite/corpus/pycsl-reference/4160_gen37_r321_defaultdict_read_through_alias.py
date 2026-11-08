r"""Test 4160 -- gen #37 route #321 (expected FAIL): `e = d; x = e[5]; 5 in d` decided False (CPython True): the read through an ALIAS inserts. Aliasing a defaultdict is REFUSED.
"""
# pycsl-expected: FAIL
from typing import Dict
from collections import defaultdict
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = defaultdict(int)
    e: Dict[int, int] = d
    x = e[5]
    if 5 in d:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 0, f()
