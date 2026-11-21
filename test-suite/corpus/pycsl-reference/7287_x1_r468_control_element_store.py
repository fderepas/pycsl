r"""Test 7287 -- route #468 CONTROL (expected PASS: PROVED at base and candidate): the imported `g(x)` only stores `x[0] = 1`, so the length is kept.
"""
# pycsl-expected: PASS
from typing import List
from multi_file_lib.x1_hc468 import g

#@ requires \length(a) == 2
#@ ensures \result == 2
def f(a: List[int]) -> int:
    g(a)
    return len(a)


if __name__ == "__main__":
    try:
        r = f([0, 0])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
