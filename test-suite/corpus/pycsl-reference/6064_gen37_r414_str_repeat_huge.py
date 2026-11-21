r"""Test 6064 -- gen #37 route #414 (expected FAIL): `"a" * n`, `requires n >= 0`, under `no_exception \all`, f(10**20) (CPython OverflowError; PROVED at base 4431ef86f).
"""
# pycsl-expected: FAIL
#@ requires n >= 0
#@ no_exception \all
def f(n: int) -> int:
    s = "a" * n
    return 0


if __name__ == "__main__":
    try:
        r = f(10**20)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
