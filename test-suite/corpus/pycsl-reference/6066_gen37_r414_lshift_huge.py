r"""Test 6066 -- gen #37 route #414 (expected FAIL): `1 << n`, `requires n >= 0`, under `no_exception \all`, f(2**64) (CPython OverflowError; PROVED at base 4431ef86f).
"""
# pycsl-expected: FAIL
#@ requires n >= 0
#@ no_exception \all
def f(n: int) -> int:
    return 1 << n


if __name__ == "__main__":
    try:
        r = f(2**64)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
