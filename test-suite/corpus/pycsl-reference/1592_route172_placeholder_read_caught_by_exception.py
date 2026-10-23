r"""Test 1592 - ROUTE #172 (gen #29): the placeholder-array read of route #171 caught by `except Exception` PROVED `\result == 0` (CPython 9) - route #171 widened only NAMED handlers below Exception. A broad handler (Exception, BaseException, bare) now widens a function that makes a claim too.
"""
# pycsl-expected: FAIL
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = []
    try:
        v = xs[0]
    except Exception:
        return 9
    return v * 0
