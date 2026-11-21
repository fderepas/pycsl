r"""Test 8015 -- route #506 (expected FAIL: PROVED at base, REFUSED PYCSL-R506-TRIGGER-SITE-UNLOWERED): un-claimed g evaluates `len((10 % n, 1))` (the tuple is modelled by its size); f's `try: return g(n, xs) except ZeroDivisionError: return 0` under `ensures \result == n + 1` -- the handler was dead in the model because the element was never evaluated; CPython f(0, [0]) returns 0
"""
# pycsl-expected: FAIL
from typing import List


#@ ensures \result == n + 1
def g(n: int, xs: List[int]) -> int:
    y = len((10 % n, 1))
    return n + 1


#@ ensures \result == n + 1
def f(n: int, xs: List[int]) -> int:
    try:
        return g(n, xs)
    except ZeroDivisionError:
        return 0


if __name__ == "__main__":
    try:
        r = f(0, [0])
        print("VIOLATION contract" if r != 1 else "result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
