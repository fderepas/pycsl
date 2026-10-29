r"""Test 7394 -- route #473 (expected PASS): CONTROL -- `c: List[int] = []; return len(c)` claiming `\result == 0` (the local size fold). PROVED at base and candidate.
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
    return len(c)


if __name__ == "__main__":
    try:
        r = h()
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
