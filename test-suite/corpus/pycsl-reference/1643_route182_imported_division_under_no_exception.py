r"""Test 1643 - ROUTE #182 (gen #29): an IMPORTED `div(x)` returning `10 // x`, called as `div(0)` under `#@ no_exception ZeroDivisionError`, PROVED (CPython ZeroDivisionError): an imported function is a trusted stub whose division is never checked. Now refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from multi_file_lib.r182_divider import div


#@ no_exception ZeroDivisionError
#@ ensures \result == 0
def probe() -> int:
    v = div(0)
    return 0
