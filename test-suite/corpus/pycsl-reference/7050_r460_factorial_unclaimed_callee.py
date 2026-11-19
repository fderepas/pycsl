r"""Test 7050 -- route #460 (expected FAIL): red-team 36 / driver repro r460 -- `math.factorial(n)` in an UN-claimed `g` called by `f` claiming `#@ no_exception \all` (CPython ValueError for f(-1)). PROVED at base 370db7dc2; now REFUSED (route #161 under g's reached claim).
"""
# pycsl-expected: FAIL
import math


def g(n: int) -> int:
    return math.factorial(n)


#@ no_exception \all
def f(n: int) -> int:
    return g(n)


if __name__ == "__main__":
    try:
        print("result", f(-1))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
