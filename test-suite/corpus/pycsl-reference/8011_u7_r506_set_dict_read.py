r"""Test 8011 -- route #506 (expected FAIL: PROVED at base, REFUSED PYCSL-R506-TRIGGER-SITE-UNLOWERED): g claims `#@ no_exception KeyError` and evaluates a set display holding `d[n]`, which the lowering models without evaluating the element, so the obligation was absent; CPython g(0, [0], {}) raises KeyError
"""
# pycsl-expected: FAIL
from typing import Dict, List


#@ no_exception KeyError
#@ ensures \result == n + 1
def g(n: int, xs: List[int], d: Dict[int, int]) -> int:
    s = {d[n]}
    return n + 1


if __name__ == "__main__":
    try:
        r = g(0, [0], {})
        print("VIOLATION contract" if r != 1 else "result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
