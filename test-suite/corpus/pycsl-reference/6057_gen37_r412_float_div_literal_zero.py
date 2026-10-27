r"""Test 6057 -- gen #37 route #412 (expected FAIL): `x / 0.0` under `no_exception \all` (CPython ZeroDivisionError; PROVED at base 4431ef86f).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(x: float) -> float:
    return x / 0.0


if __name__ == "__main__":
    try:
        r = f(1.0)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
