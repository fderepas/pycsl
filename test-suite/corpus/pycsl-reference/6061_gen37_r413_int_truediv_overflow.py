r"""Test 6061 -- gen #37 route #413 (expected FAIL): `requires b != 0`; int `a / b` under `no_exception \all`, f(10**400, 1) (CPython OverflowError; PROVED at base 4431ef86f).
"""
# pycsl-expected: FAIL
#@ requires b != 0
#@ no_exception \all
def f(a: int, b: int) -> float:
    return a / b


if __name__ == "__main__":
    try:
        r = f(10**400, 1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
