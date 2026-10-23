r"""Test 4198 -- gen #37 route #322 (expected FAIL): `sys.float_info.epsilon % 1 == 0` PROVED. REFUSED now.
"""
# pycsl-expected: FAIL
import sys
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    if sys.float_info.epsilon % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
