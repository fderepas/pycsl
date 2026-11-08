r"""Test 6574 -- route #435 (expected FAIL): `int.bit_length(x)` with `x: float`, f(1.5) (CPython TypeError) under `no_exception \all`: REFUSED (`PYCSL-R435-UNBOUND-DESCRIPTOR`). At base 78b519f63 it FAILED by accident (a Why3 type error: the float reaches an int-typed `val`), not by any check.
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(x: float) -> int:
    k = int.bit_length(x)
    return 0


if __name__ == "__main__":
    try:
        print("result", f(1.5))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
