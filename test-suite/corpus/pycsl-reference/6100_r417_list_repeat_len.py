r"""Test 6100 -- route #417 (expected FAIL): `[1, 2] * 3` lowered to a list of length 3: `len(xs) == 3` (CPython 6). PROVED at base 930d68ed5.
"""
# pycsl-expected: FAIL
#@ ensures \result == 3
#@ no_exception \all
def f() -> int:
    xs = [1, 2] * 3
    return len(xs)


if __name__ == "__main__":
    print("result", f(), "claimed 3")
