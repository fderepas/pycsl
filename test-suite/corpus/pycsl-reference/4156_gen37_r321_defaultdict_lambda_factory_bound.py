r"""Test 4156 -- gen #37 route #321 (expected FAIL): `d[1] = d[1] + 4; d[1] - 4` PROVED 0 under `defaultdict(lambda: 3)` (CPython 3). Factory REFUSED.
"""
# pycsl-expected: FAIL
from collections import defaultdict
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    d = defaultdict(lambda: 3)
    d[1] = d[1] + 4
    return d[1] - 4

if __name__ == "__main__":
    assert f() == 0, f()
