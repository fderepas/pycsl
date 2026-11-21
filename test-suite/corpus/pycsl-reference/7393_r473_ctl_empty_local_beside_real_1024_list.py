r"""Test 7393 -- route #473 (expected PASS): CONTROL -- `d = [0] * 1024` and `c = []` in ONE function: `g(d)` and `len(c) == 0`. The local `c` is attributed by the IR (its only binding is `[]`) and becomes `(Array.make 0 0)`; `d` keeps 1024. FAILED at base 1f3aa3081 (the callee saw 1024 for `c`), PROVED now.
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



#@ ensures \result == 0
#@ assigns \nothing
def h() -> int:
    d: List[int] = [0] * 1024
    c: List[int] = []
    return g(d) * 0 + ln(c)


if __name__ == "__main__":
    try:
        r = h()
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
