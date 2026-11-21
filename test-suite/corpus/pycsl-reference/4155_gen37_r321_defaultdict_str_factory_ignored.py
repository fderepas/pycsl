r"""Test 4155 -- gen #37 route #321 (expected FAIL): `defaultdict(str)[5] == 0` PROVED (CPython ''). Factory REFUSED.
"""
# pycsl-expected: FAIL
from collections import defaultdict
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    d = defaultdict(str)
    if d[5] == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
