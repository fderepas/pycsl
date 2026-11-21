r"""Test 7432 -- cv6 D1 (expected FAIL, refused): `max(len(xs), xs.append(1) or 0)` -- a list mutator inside a later call operand. UNEXPECTED PIPELINE ERROR (maximum recursion depth) at base 4d15b89a7 (same failed-probe loop as 7430); now the in-place-mutator refusal. CPython: f([]) returns 1.
"""
# pycsl-expected: FAIL
from typing import List


#@ requires len(xs) == 0
#@ ensures \result == 0
#@ assigns \nothing
def f(xs: List[int]) -> int:
    n = max(len(xs), xs.append(1) or 0)
    return len(xs)


if __name__ == "__main__":
    try:
        r = f([])
        print("result", r, "VIOLATION" if r != 0 else "")
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
