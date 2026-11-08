r"""Test 3383 -- route #289 (expected FAIL): red-team a028: `t: Tuple[List[int], int] = (xs, 0); b = t[0]; b[0] = 5; return xs[0]` PROVED `\old(xs[0])` (the tuple is `any int`, the store a no-effect `subscript_set`); CPython: 5. Now refused (PYCSL-SEM-STORE-THROUGH-OPAQUE-ELEMENT).
"""
# pycsl-expected: FAIL
from typing import List, Tuple


#@ requires \length(xs) == 1
#@ ensures \result == \old(xs[0])
def f(xs: List[int]) -> int:
    t: Tuple[List[int], int] = (xs, 0)
    b = t[0]
    b[0] = 5
    return xs[0]


if __name__ == "__main__":
    assert f([1]) == 5
