r"""Test 4200 -- gen #37 route #324 (expected FAIL): `ensures \result == len(s[1:-1])` with `return 0` PROVED (raw `String.substring s 1 (-1-1)` is ""; CPython 1).
"""
# pycsl-expected: FAIL
#@ requires len(s) == 3
#@ ensures \result == len(s[1:-1])
#@ assigns \nothing
def f(s: str) -> int:
    return 0

if __name__ == "__main__":
    assert f("abc") == len("abc"[1:-1]), f("abc")
