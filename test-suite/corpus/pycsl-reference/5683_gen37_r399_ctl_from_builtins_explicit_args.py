r"""Test 5683 -- gen #37 CONTROL route #399 (expected PASS): `from builtins import sum` called with explicit arguments; PROVED (CPython 3).
"""
# pycsl-expected: PASS
from builtins import sum
#@ ensures \result == 3
def f() -> int:
    return sum([1, 2])
if __name__ == "__main__":
    assert f() == 3
