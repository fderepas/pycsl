r"""Test 1549 - ROUTE #160 (gen #29): `pow(0, -1)` under `no_exception ZeroDivisionError` PROVED (the `**` row is wired, the `pow()` call is not); CPython raises. Refused unless the exponent is a non-negative literal or the base a nonzero literal.
"""
# pycsl-expected: FAIL
from typing import List
_ = 0  # anchor


#@ no_exception ZeroDivisionError
def probe() -> int:
    return pow(0, -1)

