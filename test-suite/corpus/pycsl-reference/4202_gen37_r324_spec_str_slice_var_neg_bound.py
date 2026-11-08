r"""Test 4202 -- gen #37 route #324 (expected FAIL): `len(s[0:i])` with `i == -1` and `return 0` PROVED (CPython 2).
"""
# pycsl-expected: FAIL
#@ requires len(s) == 3 and i == -1
#@ ensures \result == len(s[0:i])
#@ assigns \nothing
def f(s: str, i: int) -> int:
    return 0

if __name__ == "__main__":
    assert f("abc", -1) == len("abc"[0:-1]), f("abc", -1)
