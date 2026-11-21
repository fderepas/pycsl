r"""Test 1645 - ROUTE #182 control (gen #29): calling the imported `div` in a function with no ZeroDivisionError context is unaffected: `v - v + 5 == 5` proves over its result.
"""
_ = 0  # anchor
from multi_file_lib.r182_divider import div


#@ ensures \result == 5
def probe() -> int:
    v = div(2)
    return v - v + 5
