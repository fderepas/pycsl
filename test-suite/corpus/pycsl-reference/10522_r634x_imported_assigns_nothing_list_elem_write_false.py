r"""Test 10522 -- run #9 u76, review rt84 F2, route #634. The helper zu76d.f declares `#@ assigns
\nothing` but writes xs[0] of its list parameter inside a loop; the caller assumes xs[0] unchanged. `cd <tree
root> && python <this file>` prints "CPython g([0]) = 5", the claim below is false. REFUSED:
PYCSL-FUNCTION-FRAME.
"""
# pycsl-expected: FAIL
from typing import List
from zu76d import f


#@ requires len(xs) >= 1 and xs[0] == 0
#@ ensures \result == 0
def g(xs: List[int]) -> int:
    f(xs)
    return xs[0]


if __name__ == "__main__":
    print("CPython g([0]) =", g([0]))
