r"""Test 4151 -- gen #37 route #321 (expected FAIL): `defaultdict(int, d)` before and after `d = {1: 6}` shared one constant; decided equal (CPython 5 vs 6). Non-literal seed REFUSED.
"""
# pycsl-expected: FAIL
from collections import defaultdict
from typing import Dict
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    d = {1: 5}
    a: Dict[int, int] = defaultdict(int, d)
    d = {1: 6}
    b: Dict[int, int] = defaultdict(int, d)
    if a[1] != b[1]:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 0, f()
