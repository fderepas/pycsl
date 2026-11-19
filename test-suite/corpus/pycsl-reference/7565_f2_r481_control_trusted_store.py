r"""Test 7565 -- route #481 CONTROL (expected PASS: PROVED at base and candidate): the same-file `\trusted` `k(xs)` only stores `xs[0] = 1`, so the length is kept.
"""
# pycsl-expected: PASS
from typing import List


#@ \trusted
def k(xs: List[int]) -> int:
    xs[0] = 1
    return 0


#@ requires \length(xs) >= 1
#@ ensures \result == \old(\length(xs))
def f(xs: List[int]) -> int:
    k(xs)
    return len(xs)


if __name__ == "__main__":
    try:
        r = f([0])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
