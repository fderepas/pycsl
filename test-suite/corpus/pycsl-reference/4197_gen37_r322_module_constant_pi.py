r"""Test 4197 -- gen #37 route #322 (expected FAIL): module-level `PI = math.pi`; `PI % 1 == 0` PROVED. REFUSED now.
"""
# pycsl-expected: FAIL
import math
PI = math.pi

#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    if PI % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
