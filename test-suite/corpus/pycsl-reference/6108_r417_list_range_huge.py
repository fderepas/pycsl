r"""Test 6108 -- route #417 (expected FAIL): `list(range(n))`, `requires n >= 0`, under `no_exception \all`, f(10**20) (CPython OverflowError). PROVED at base 930d68ed5.
"""
# pycsl-expected: FAIL
#@ requires n >= 0
#@ no_exception \all
def f(n: int) -> int:
    xs = list(range(n))
    return 0


if __name__ == "__main__":
    try:
        print(f(10**20))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
