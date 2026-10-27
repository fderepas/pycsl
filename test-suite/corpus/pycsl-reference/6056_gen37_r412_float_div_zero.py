r"""Test 6056 -- gen #37 route #412 (expected FAIL): `x / y` over floats under `no_exception \all`, f(1.0, 0.0) (CPython ZeroDivisionError; PROVED at base 4431ef86f).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(x: float, y: float) -> float:
    return x / y


if __name__ == "__main__":
    try:
        r = f(1.0, 0.0)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
