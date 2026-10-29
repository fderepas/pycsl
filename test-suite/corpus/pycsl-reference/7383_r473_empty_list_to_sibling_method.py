r"""Test 7383 -- route #473 (expected FAIL): `c: List[int] = []; x = self.g(c); return x * 0` -- a sibling method call (the R167 stubbed-call assertion read `Array.length c >= 1` against 1024). PROVED at base 1f3aa3081; CPython IndexError; now FAILS.
"""
# pycsl-expected: FAIL
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



class M:
    #@ requires len(c) >= 1
    #@ assigns \nothing
    def g(self, c: List[int]) -> int:
        return c[0]

    #@ ensures \result == 0
    #@ assigns \nothing
    def h(self) -> int:
        c: List[int] = []
        x = self.g(c)
        return x * 0


if __name__ == "__main__":
    try:
        r = M().h()
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
