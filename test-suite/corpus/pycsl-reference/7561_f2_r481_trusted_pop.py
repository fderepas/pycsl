r"""Test 7561 -- route #481 (expected FAIL: PROVED at base, REFUSED): a same-file `\trusted` `k(xs)` with no `assigns` pops; CPython returns 0.
"""
# pycsl-expected: FAIL
from typing import List


#@ \trusted
def k(xs: List[int]) -> int:
    xs.pop()
    return 0


#@ requires \length(xs) >= 1
#@ ensures \result == \old(\length(xs))
def f(xs: List[int]) -> int:
    k(xs)
    return len(xs)


if __name__ == "__main__":
    try:
        r = f([0])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
