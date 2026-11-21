r"""Test 1622 - ROUTE #177 (gen #29): `sum(10 // x for x in xs)` with `xs = [0, 1]` under `#@ no_exception ZeroDivisionError` PROVED (CPython ZeroDivisionError).
"""
# pycsl-expected: FAIL
from typing import List
_ = 0  # anchor


#@ no_exception ZeroDivisionError
#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [0, 1]
    t = sum(10 // x for x in xs)
    return 0
