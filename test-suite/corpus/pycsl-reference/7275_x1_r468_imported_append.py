r"""Test 7275 -- route #468 (red team 38, expected FAIL: PROVED at base, REFUSED): an un-contracted imported `g(x)` appends; `len(a)` is 3 in CPython.
"""
# pycsl-expected: FAIL
from typing import List
from multi_file_lib.x1_h468a import g

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
