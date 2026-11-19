r"""Test 7392 -- route #473 (expected PASS): CONTROL -- a REAL 1024-element list `c: List[int] = [0] * 1024` handed to `g` and `ln`, claiming `\result == 1024`: the same text `(Array.make 1024 0)` is left alone (the IR names it a list repetition). PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import List, Tuple


#@ requires len(c) >= 1
#@ ensures \result == c[0]
#@ assigns \nothing
def g(c: List[int]) -> int:
    return c[0]


#@ ensures \result == len(c)
#@ assigns \nothing
def ln(c: List[int]) -> int:
    return len(c)



#@ ensures \result == 1024
#@ assigns \nothing
def h() -> int:
    c: List[int] = [0] * 1024
    return g(c) + ln(c)


if __name__ == "__main__":
    try:
        r = h()
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
