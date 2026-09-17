r"""Test 1591 - ROUTE #171 control (gen #29): an in-bounds read inside a try with an IndexError handler still proves `\result == 2`.
"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    xs: List[int] = [1, 2]
    try:
        v = xs[1]
    except IndexError:
        return 9
    return v
