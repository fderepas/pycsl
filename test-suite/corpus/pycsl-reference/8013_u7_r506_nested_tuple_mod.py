r"""Test 8013 -- route #506 (expected FAIL: PROVED at base, REFUSED PYCSL-R506-TRIGGER-SITE-UNLOWERED): g claims `#@ no_exception ZeroDivisionError` and evaluates a nested tuple display `((10 % n, 1), 2)`, which the lowering models without evaluating the element, so the obligation was absent; CPython g(0, [0], {}) raises ZeroDivisionError
"""
# pycsl-expected: FAIL
from typing import Dict, List


#@ no_exception ZeroDivisionError
#@ ensures \result == n + 1
def g(n: int, xs: List[int], d: Dict[int, int]) -> int:
    t = ((10 % n, 1), 2)
    return n + 1


if __name__ == "__main__":
    try:
        r = g(0, [0], {})
        print("VIOLATION contract" if r != 1 else "result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
