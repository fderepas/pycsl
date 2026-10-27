r"""Test 6113 -- route #417 (expected FAIL): `float(g(n))` of a user function's int result under `no_exception \all`, f(10**400) (CPython OverflowError): not positively int-read, so REFUSED (`PYCSL-R417-UNCHECKED-FLOAT-CONVERSION`). PROVED at base 930d68ed5.
"""
# pycsl-expected: FAIL
#@ ensures \result == n
#@ no_exception \all
def g(n: int) -> int:
    return n


#@ no_exception \all
def f(n: int) -> int:
    x = float(g(n))
    return 0


if __name__ == "__main__":
    try:
        print(f(10**400))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
