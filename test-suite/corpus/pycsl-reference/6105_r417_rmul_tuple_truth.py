r"""Test 6105 -- route #417 (expected FAIL): `3 * (0,)` lowered to the int `3 * 0`: `if t:` decided False (CPython truthy, returns 1). PROVED at base 930d68ed5.
"""
# pycsl-expected: FAIL
#@ ensures \result == 0
#@ no_exception \all
def f() -> int:
    t = 3 * (0,)
    if t:
        return 1
    return 0


if __name__ == "__main__":
    print("result", f(), "claimed 0")
