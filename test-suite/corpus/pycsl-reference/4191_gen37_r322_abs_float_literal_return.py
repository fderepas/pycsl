r"""Test 4191 -- gen #37 route #322 (expected FAIL): `return abs(2.5)` with `ensures \result == 2` PROVED (CPython 2.5).
"""
# pycsl-expected: FAIL
#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    return abs(2.5)

if __name__ == "__main__":
    assert f() == 2, f()
