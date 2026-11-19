r"""Test 6609 -- route #438 (expected FAIL): red team 34 y13: `hash(k)` with `k = g2(t)`, `g2(..) -> tuple`. PROVED at base 1c083dcbe (= 78b519f63 emission); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R349-UNDERIVABLE-HASH-UNDER-CLAIM).
"""
# pycsl-expected: FAIL
from typing import List, Tuple

def g2(t: Tuple[List[int], int]) -> tuple:
    return t


#@ no_exception \all
def f(t: Tuple[List[int], int]) -> int:
    k = g2(t)
    return hash(k)


if __name__ == "__main__":
    try:
        r = f(([1], 1))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
