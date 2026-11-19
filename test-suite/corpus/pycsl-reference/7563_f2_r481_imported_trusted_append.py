r"""Test 7563 -- route #481 (expected FAIL: PROVED at base, REFUSED): an imported explicit `\trusted` `k_grow(xs)` appends; CPython returns 2.
"""
# pycsl-expected: FAIL
from typing import List
from multi_file_lib.f2_h481 import k_grow


#@ requires \length(xs) >= 1
#@ ensures \result == \old(\length(xs))
def f(xs: List[int]) -> int:
    k_grow(xs)
    return len(xs)


if __name__ == "__main__":
    try:
        r = f([0])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
