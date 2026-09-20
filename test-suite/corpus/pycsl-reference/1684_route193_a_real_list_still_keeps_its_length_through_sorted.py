r"""Test 1684 - ROUTE #193 control (gen #30): making the placeholder opaque costs a REAL array nothing. `sorted` of a genuine three-element list still carries its length through `sorted_1`'s `Array.length result = Array.length a`, so `len(sorted(ys)) == 3` still proves. The repair removes a length the model never knew, not one it did.
"""
from typing import List

_ = 0  # anchor


#@ ensures \result == 3
def probe() -> int:
    ys: List[int] = [3, 1, 2]
    xs: List[int] = sorted(ys)
    return len(xs)
