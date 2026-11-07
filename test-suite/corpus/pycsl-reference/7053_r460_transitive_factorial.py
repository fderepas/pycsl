r"""Test 7053 -- route #460 (expected FAIL): the reach is TRANSITIVE -- `f` (claiming `#@ no_exception ValueError`) calls an un-claimed `g`, which calls an un-claimed `h` holding `math.factorial(n)` (CPython ValueError for f(-2)). PROVED at base 370db7dc2; now REFUSED in h.
"""
# pycsl-expected: FAIL
import math


def h(n: int) -> int:
    return math.factorial(n)


def g(n: int) -> int:
    return h(n) + 1


#@ no_exception ValueError
def f(n: int) -> int:
    return g(n)


if __name__ == "__main__":
    try:
        print("result", f(-2))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
