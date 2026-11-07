r"""Test 6110 -- route #417 (expected FAIL): `float(n)` of an int under `no_exception \all`, f(10**400) (CPython OverflowError). PROVED at base 930d68ed5.
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(n: int) -> int:
    x = float(n)
    return 0


if __name__ == "__main__":
    try:
        print(f(10**400))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
