r"""Test 7963 -- route #502 (expected FAIL: PROVED at base, REFUSED PYCSL-R502-CALLEE-COMPREHENSION-OBLIGATION): h's `{10 % v for v in xs}` reached through g (depth 2); f catches ZeroDivisionError; CPython returns 2
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional

#@ ensures \result == 1
def h(xs: List[int]) -> int:
    s = {10 % v for v in xs}
    return 1


#@ ensures \result == 1
def g(xs: List[int]) -> int:
    return h(xs)


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
