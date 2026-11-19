r"""Test 6103 -- route #417 (expected FAIL): `(0,) * 3` lowered to the int `0 * 3`: `if t:` decided False (CPython `(0, 0, 0)` is truthy, returns 1). PROVED at base 930d68ed5.
"""
# pycsl-expected: FAIL
#@ ensures \result == 0
#@ no_exception \all
def f() -> int:
    t = (0,) * 3
    if t:
        return 1
    return 0


if __name__ == "__main__":
    print("result", f(), "claimed 0")
