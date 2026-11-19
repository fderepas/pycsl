r"""Test 4190 -- gen #37 route #322 (expected FAIL): `abs(2.5) == 2` folded via `abs(int(2.5))` and PROVED (CPython 2.5 != 2).
"""
# pycsl-expected: FAIL
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    if abs(2.5) == 2:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
