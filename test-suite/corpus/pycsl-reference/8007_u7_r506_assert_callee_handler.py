r"""Test 8007 -- route #506 (expected FAIL: PROVED at base, REFUSED PYCSL-R506-TRIGGER-SITE-UNLOWERED): un-claimed g evaluates an `assert 10 // n >= 0 or True` test; f's `try: return g(n, xs) except ZeroDivisionError: return 0` under `ensures \result == n + 1` -- the handler was dead in the model because the element was never evaluated; CPython f(0, [0]) returns 0
"""
# pycsl-expected: FAIL
from typing import List


#@ ensures \result == n + 1
def g(n: int, xs: List[int]) -> int:
    assert 10 // n >= 0 or True
    return n + 1


#@ ensures \result == n + 1
def f(n: int, xs: List[int]) -> int:
    try:
        return g(n, xs)
    except ZeroDivisionError:
        return 0


if __name__ == "__main__":
    r = f(0, [0])
    print("VIOLATION contract" if r != 1 else "result", r)
