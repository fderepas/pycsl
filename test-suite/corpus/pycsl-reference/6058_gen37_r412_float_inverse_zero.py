r"""Test 6058 -- gen #37 route #412 (expected FAIL): `1.0 / (x - x)` under `no_exception \all` (CPython ZeroDivisionError; PROVED at base 4431ef86f).
"""
# pycsl-expected: FAIL
#@ requires x > 0.0
#@ no_exception \all
def f(x: float) -> float:
    return 1.0 / (x - x)


if __name__ == "__main__":
    try:
        r = f(1.0)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
