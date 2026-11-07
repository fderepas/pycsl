r"""Test 4154 -- gen #37 route #321 (expected FAIL): `defaultdict(lambda: 7)[5] == 0` PROVED (CPython 7). Factories other than `int` / `lambda: 0` are REFUSED.
"""
# pycsl-expected: FAIL
from collections import defaultdict
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    d = defaultdict(lambda: 7)
    if d[5] == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
