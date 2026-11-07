r"""Test 6101 -- route #417 (expected FAIL): `[1, 2] * 3` lowered to `Array.make 3 1`: `xs[1] == 1` (CPython 2). PROVED at base 930d68ed5.
"""
# pycsl-expected: FAIL
#@ ensures \result == 1
#@ no_exception \all
def f() -> int:
    xs = [1, 2] * 3
    return xs[1]


if __name__ == "__main__":
    print("result", f(), "claimed 1")
