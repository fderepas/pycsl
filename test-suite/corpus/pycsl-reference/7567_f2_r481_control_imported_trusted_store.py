r"""Test 7567 -- route #481 CONTROL (expected PASS: PROVED at base and candidate): the imported explicit `\trusted` `k_store(xs)` only stores an element.
"""
# pycsl-expected: PASS
from typing import List
from multi_file_lib.f2_h481 import k_store


#@ requires \length(xs) >= 1
#@ ensures \result == \old(\length(xs))
def f(xs: List[int]) -> int:
    k_store(xs)
    return len(xs)


if __name__ == "__main__":
    try:
        r = f([0])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
