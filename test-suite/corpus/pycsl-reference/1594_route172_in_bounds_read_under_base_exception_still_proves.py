r"""Test 1594 - ROUTE #172 control (gen #29): an in-bounds read inside a try with `except BaseException` still proves `\result == 2`.
"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    xs: List[int] = [1, 2]
    try:
        v = xs[1]
    except BaseException:
        return 9
    return v
