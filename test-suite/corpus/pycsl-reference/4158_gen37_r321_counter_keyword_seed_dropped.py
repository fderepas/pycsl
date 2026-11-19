r"""Test 4158 -- gen #37 route #321 (expected FAIL): `Counter(a=5)['a'] == 0` PROVED (CPython 5). Keyword REFUSED.
"""
# pycsl-expected: FAIL
from collections import Counter
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    c = Counter(a=5)
    if c["a"] == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
