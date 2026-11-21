r"""Test 7964 -- route #502 (expected FAIL: refused at base by route #252, REFUSED PYCSL-R502-CALLEE-COMPREHENSION-OBLIGATION): a method `C.g` holds `[10 // v for v in xs]` and is reached as `c.g(xs)` on a `C` parameter; f catches ZeroDivisionError; CPython returns 2
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional

class C:
    #@ ensures \result == 1
    def g(self, xs: List[int]) -> int:
        ys = [10 // v for v in xs]
        return 1


#@ ensures \result == 1
def f(c: C, xs: List[int]) -> int:
    try:
        return c.g(xs)
    except ZeroDivisionError:
        return 2


if __name__ == "__main__":
    try:
        r = f(C(), [0])
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
