r"""Test 7564 -- route #481 (expected FAIL: PROVED at base, REFUSED): a `\trusted` METHOD `C.k(self, xs)` appends to its list parameter; CPython returns 2.
"""
# pycsl-expected: FAIL
from typing import List


class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ \trusted
    def k(self, xs: List[int]) -> int:
        xs.append(1)
        return 0


#@ requires \length(xs) >= 1
#@ ensures \result == \old(\length(xs))
def f(c: C, xs: List[int]) -> int:
    c.k(xs)
    return len(xs)


if __name__ == "__main__":
    try:
        r = f(C(), [0])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
