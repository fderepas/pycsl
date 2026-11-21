r"""Test 6109 -- route #417 (expected FAIL): `for x in sorted(range(n))`, `requires n >= 0`, under `no_exception \all`, g(10**20) (CPython OverflowError; the iterable was erased to `(any int)`). PROVED at base 930d68ed5.
"""
# pycsl-expected: FAIL
#@ requires n >= 0
#@ no_exception \all
def g(n: int) -> int:
    c = 0
    for x in sorted(range(n)):
        c = 1
    return 0


if __name__ == "__main__":
    try:
        print(g(10**20))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
