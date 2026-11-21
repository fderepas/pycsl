r"""Test 4192 -- gen #37 route #322 (expected FAIL): `x = abs(0.5); x == 0` PROVED (CPython 0.5).
"""
# pycsl-expected: FAIL
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    x = abs(0.5)
    if x == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
