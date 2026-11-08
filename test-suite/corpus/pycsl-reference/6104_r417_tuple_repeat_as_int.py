r"""Test 6104 -- route #417 (expected FAIL): `(1,) * n` lowered to the int product: `\result == n` (CPython returns a tuple). PROVED at base 930d68ed5.
"""
# pycsl-expected: FAIL
#@ requires n >= 2 and n <= 10
#@ ensures \result == n
#@ no_exception \all
def f(n: int) -> int:
    t = (1,) * n
    return t


if __name__ == "__main__":
    print("result", f(3), "claimed 3")
