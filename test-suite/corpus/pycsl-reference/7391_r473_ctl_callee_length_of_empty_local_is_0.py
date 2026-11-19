r"""Test 7391 -- route #473 (expected PASS): CONTROL -- 7388 with CPython's own answer `\result == 0`: FAILED at base 1f3aa3081 (the callee saw 1024), PROVED now.
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
    c: List[int] = []
    return ln(c)


if __name__ == "__main__":
    try:
        r = h()
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
