r"""Test 7566 -- route #481 CONTROL (expected PASS: PROVED at base and candidate): the same-file `\trusted` `k(xs)` with `assigns xs` reads `len(xs)` and stores an element only.
"""
# pycsl-expected: PASS
from typing import List


#@ \trusted
#@ assigns xs
def k(xs: List[int]) -> int:
    if len(xs) > 0 and xs[0] == 3:
        xs[0] = 4
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
