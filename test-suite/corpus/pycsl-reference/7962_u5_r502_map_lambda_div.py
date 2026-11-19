r"""Test 7962 -- route #502 (expected FAIL: NOT PROVED at base (Why3 failure), REFUSED PYCSL-R502-CALLEE-COMPREHENSION-OBLIGATION): g's `list(map(lambda v: 10 // v, xs))`; f catches ZeroDivisionError; CPython returns 2
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional

#@ ensures \result == 1
def g(xs: List[int]) -> int:
    ys = list(map(lambda v: 10 // v, xs))
    return 1


#@ ensures \result == 1
def f(xs: List[int]) -> int:
    try:
        return g(xs)
    except ZeroDivisionError:
        return 2


if __name__ == "__main__":
    try:
        r = f([0])
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
