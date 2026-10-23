r"""Test 1644 - ROUTE #182 (gen #29): the imported `div(0)` inside `try ... except ZeroDivisionError: return 9` PROVED `\result == 0` (CPython 9).
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from multi_file_lib.r182_divider import div


#@ ensures \result == 0
def probe() -> int:
    try:
        v = div(0)
    except ZeroDivisionError:
        return 9
    return 0
